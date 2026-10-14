# Copyright 2024
# Directory: yt-rag/app/services/emi.py

"""
EMI (Equated Monthly Instalment) calculator service.

Standard reducing-balance formula:

    EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)

where:
    P = principal (loan amount)
    r = monthly interest rate  (annual_rate / 12 / 100)
    n = tenure in months

Returns the monthly instalment, total interest and total payment, an optional
processing-fee-adjusted cost, and a full month-by-month amortization schedule
so the frontend can render the graph + table without re-computing anything.

Pure Python + math — no external dependencies, safe to call synchronously.
"""

import logging
import math
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

logger = logging.getLogger(__name__)

MONEY = Decimal("0.01")


def _round2(value: float) -> float:
    """Round a float to 2 decimal places (currency)."""
    return float(Decimal(str(value)).quantize(MONEY, rounding=ROUND_HALF_UP))


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Compute the flat monthly EMI for a reducing-balance loan."""
    if principal <= 0 or tenure_months <= 0:
        raise ValueError("principal and tenure_months must be positive")
    monthly_rate = annual_rate / 12.0 / 100.0
    if monthly_rate == 0:
        return _round2(principal / tenure_months)
    factor = (1.0 + monthly_rate) ** tenure_months
    return _round2(principal * monthly_rate * factor / (factor - 1.0))


def emi_schedule(principal: float, annual_rate: float, tenure_months: int) -> List[dict]:
    """
    Build the full amortization schedule (monthly: interest, principal, balance).

    The final row's principal is nudged to close on the exact balance so the
    schedule always sums back to the original principal.
    """
    monthly_rate = annual_rate / 12.0 / 100.0
    emi = calculate_emi(principal, annual_rate, tenure_months)
    balance = float(principal)
    schedule: List[dict] = []
    for month in range(1, tenure_months + 1):
        interest = _round2(balance * monthly_rate)
        principal_part = _round2(emi - interest)
        if month == tenure_months:
            principal_part = _round2(balance)
        balance = _round2(balance - principal_part)
        if balance < 0:
            balance = 0.0
        schedule.append({
            "month": month,
            "emi": emi,
            "interest": _round2(interest),
            "principal": _round2(principal_part),
            "balance": balance,
        })
    return schedule


def calculate(
    principal: float,
    annual_rate: float,
    tenure_months: int,
    processing_fee_percent: float = 0.0,
    include_schedule: bool = True,
) -> dict:
    """
    Full EMI breakdown.

    Returns dict with:
      principal, annual_rate, tenure_months, monthly_rate,
      emi, total_interest, total_payment,
      processing_fee, effective_borrowing, effective_annual_rate (approx), and
      schedule (optional month-by-month rows).
    """
    if principal <= 0:
        raise ValueError("loan amount must be greater than 0")
    if annual_rate < 0:
        raise ValueError("interest rate cannot be negative")
    if tenure_months <= 0:
        raise ValueError("tenure must be greater than 0 months")
    if annual_rate == 0:
        emi = _round2(principal / tenure_months)
        total_payment = _round2(emi * tenure_months)
    else:
        emi = calculate_emi(principal, annual_rate, tenure_months)
        total_payment = _round2(emi * tenure_months)

    total_interest = _round2(total_payment - principal)
    processing_fee = _round2(principal * processing_fee_percent / 100.0)

    # Effective cost: fee reduces the amount actually received. We approximate
    # the true APR on the net disbursal with a simple Newton iteration.
    net_disbursal = principal - processing_fee
    effective_annual_rate = 0.0
    if net_disbursal > 0:
        effective_annual_rate = _approx_apr(net_disbursal, emi, tenure_months)

    result = {
        "principal": _round2(principal),
        "annual_rate": annual_rate,
        "tenure_months": tenure_months,
        "monthly_rate": round(annual_rate / 12.0, 4),
        "emi": emi,
        "total_interest": total_interest,
        "total_payment": total_payment,
        "processing_fee_percent": processing_fee_percent,
        "processing_fee": processing_fee,
        "net_disbursal": _round2(net_disbursal),
        "effective_annual_rate": round(effective_annual_rate, 2),
    }

    if include_schedule:
        result["schedule"] = emi_schedule(principal, annual_rate, tenure_months)

    logger.info(
        "EMI computed principal=%s rate=%s%% tenure=%sm → emi=%s",
        principal, annual_rate, tenure_months, emi,
    )
    return result


def _approx_apr(net_disbursal: float, emi: float, tenure_months: int, tolerance: float = 1e-6) -> float:
    """Estimate the annual interest rate on net disbursal (solve for pv(rate)=net)."""
    def npv(monthly_rate: float) -> float:
        total = 0.0
        for t in range(1, tenure_months + 1):
            total += emi / (1.0 + monthly_rate) ** t
        return net_disbursal - total

    if net_disbursal <= 0 or emi <= 0:
        return 0.0
    # npv increases with rate: at 0% the PV is emi*n (max), so npv(0) <= 0.
    low, high = 0.0, 1.0
    if npv(0) >= 0:
        return 0.0
    while npv(high) < 0 and high < 1.0:
        high = min(high * 2.0, 1.0)
    iterations = 0
    while high - low > tolerance and iterations < 200:
        mid = (low + high) / 2.0
        if npv(mid) < 0:
            low = mid
        else:
            high = mid
        iterations += 1
    monthly_rate = (low + high) / 2.0
    return monthly_rate * 1200.0