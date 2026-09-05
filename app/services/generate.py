# Copyright 2024
# Directory: yt-rag/app/services/generate.py

"""
AI auto-generation engine for Sahayak.

After a user completes a chat session, this service turns the final
question + the RAG explainer's cited answer + the applicant profile into a
structured bundle:

  * a plain-language "recommendation" summary (which schemes are worth
    checking, why, and hedged — this is NOT an eligibility verdict),
  * a per-user dashboard payload (stats, cited sources, matched schemes),
  * a documentation page (scheme list, document checklist, next steps).

It is driven through Groq (OpenAI-compatible). The generated JSON is saved
to the Supabase `user_sessions` table on a best-effort basis so the Results,
Dashboard and Documentation pages can reload it later.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

import openai

from ..core.config import get_settings
from ..core.database import db

logger = logging.getLogger(__name__)
settings = get_settings()


# Mirrors chat.py's hard rule: the LLM explains and cites; it never decides
# eligibility. Auto-generated output must keep hedged wording and only restate
# what is in the retrieved/cited context.
GENERATE_PROMPT = """You are the auto-generation engine for Sahayak, an assistant helping \
marginalized entrepreneurs (SC, OBC, ST, DNT, Safai Karamcharis, transgender persons, PwD, and \
women from marginalized communities) understand Indian government business-support schemes.

A user has just completed a chat with the RAG explainer. Your job is to produce ONE structured \
JSON object that powers their personalised Results page, Dashboard and Documentation page.

HARD RULES:
1. Base everything ONLY on the provided applicant profile, the user's question, and the cited \
answer. Never invent schemes, amounts, deadlines, interest rates, or eligibility criteria.
2. NEVER declare that someone "is eligible", "will receive", "is approved", or "qualifies". Use \
hedged phrasing like "may fit", "per the stated criteria", "check with the bank/department".
3. Keep scheme names, benefits and document needs faithful to the cited answer.
4. Write the human-facing text in the SAME language as the user's question (Hindi, English, or \
Hinglish).
5. Return ONLY valid JSON with no prose before or after. Do not wrap in markdown code fences.

JSON schema (all keys required):
{
  "language": "hi|en",
  "recommendation_summary": "one short paragraph (2-3 sentences) answering 'which schemes may be worth checking and why; check with the bank for final eligibility'",
  "matched_schemes": [
    {
      "name": "scheme name",
      "why": "one-two sentences why it may fit the user's profile/goal (hedged)",
      "citations": ["chunk_id_from_answer"]
    }
  ],
  "top_match": "name of the single most likely-fitted scheme from matched_schemes",
  "document_checklist": ["document1", "document2"],
  "next_steps": ["step1", "step2", "step3"],
  "dashboard": {
    "goal": "one line restating the user's business goal",
    "category": "user category or 'Not specified'",
    "schemes_considered": "count as number",
    "sources_cited": "count as number",
    "full_name": "user full name if provided else 'Guest'"
  }
}
"""


def _extract_json(text: str) -> Dict[str, Any]:
    """Robustly pull a JSON object out of the model's response."""
    t = (text or "").strip()
    # Strip markdown code fences (```json ... ```) wherever they appear.
    t = re.sub(r"```(?:json)?", "", t, flags=re.IGNORECASE)
    t = t.replace("```", "")
    t = t.strip()
    try:
        return json.loads(t)
    except Exception:
        pass
    # Fallback: scan for a balanced '{' ... '}' JSON object anywhere in the text
    # (handles surrounding prose and stray trailing text).
    for i, ch in enumerate(t):
        if ch != "{":
            continue
        depth = 0
        in_str = False
        esc = False
        for j in range(i, len(t)):
            c = t[j]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
                continue
            if c == '"':
                in_str = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    candidate = t[i:j + 1]
                    try:
                        return json.loads(candidate)
                    except Exception:
                        break
    raise ValueError("Could not parse JSON from generation output")


class GenerateService:
    """Auto-generates Results/Dashboard/Documentation data from a completed chat."""

    def __init__(self):
        # Groq exposes an OpenAI-compatible API; reuse the chat config.
        self.client = openai.OpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url,
        )
        self.model = settings.groq_chat_model

    def _build_user_prompt(self, query: str, answer: str,
                           citations: List[str], profile: Optional[Dict[str, Any]]) -> str:
        profile_lines = "\n".join(
            f"- {k}: {v}" for k, v in (profile or {}).items() if v
        ) if profile else "- (none provided)"
        return (
            "Applicant profile:\n" + profile_lines +
            "\n\nUser's question:\n" + query +
            "\n\nRAG explainer's cited answer:\n" + answer +
            "\n\nCited chunk ids:\n" + ", ".join(citations or []) +
            "\n\nGenerate the JSON per the schema."
        )

    async def generate(self, query: str, answer: str,
                       citations: List[str],
                       profile: Optional[Dict[str, Any]] = None,
                       user_id: Optional[str] = None,
                       user_email: Optional[str] = None) -> Dict[str, Any]:
        """Return the structured generated bundle."""
        user_prompt = self._build_user_prompt(query, answer, citations, profile)

        data = None
        last_err = None
        for attempt in range(settings.gemini_max_retries):
            raw = ""
            last_err = None
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": GENERATE_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2,
                    max_tokens=1400,
                )
                raw = resp.choices[0].message.content or ""
                data = _extract_json(raw)
                data = self._fill_defaults(data, profile, citations)
                break
            except Exception as e:
                last_err = e
                msg = (getattr(e, "message", "") + " " + str(getattr(e, "status_code", ""))).lower()
                transient = any(k in msg for k in ("429", "503", "unavailable", "rate", "overloaded"))
                # Retry on transient API errors AND on unparseable output (the
                # LLM sometimes returns prose/dangling JSON — a fresh attempt
                # usually returns clean JSON).
                if attempt < settings.gemini_max_retries - 1:
                    if transient:
                        import time
                        wait = (attempt + 1) * settings.gemini_retry_delay
                        logger.warning(f"generate: transient error, retry {attempt + 1} in {wait}s: {e}")
                        time.sleep(wait)
                    else:
                        logger.warning(f"generate: unparseable output, retrying ({attempt + 1}): {raw[:1200]!r}")
                    continue
        if data is None:
            raise last_err if last_err else ValueError("Generation returned no usable output")

        result = {
            "query": query,
            "profile": profile or {},
            "generated": data,
            "user_id": user_id,
            "user_email": user_email,
        }
        await self._persist(result)
        return result

    @staticmethod
    def _fill_defaults(data: Dict[str, Any], profile: Optional[Dict[str, Any]],
                       citations: Optional[List[str]] = None) -> Dict[str, Any]:
        """Ensure the generated bundle is never missing key fields (esp. docs)."""
        if data.get("document_checklist") is None or not data["document_checklist"]:
            # Common documents for Indian government scheme applications.
            docs = ["Identity proof (Aadhaar)", "Address proof",
                    "Photograph", "Bank account details"]
            cat = (profile or {}).get("category")
            if cat and cat not in ("General", "Other"):
                docs.append("Category certificate (" + cat + ")")
            if (profile or {}).get("business_stage", "").lower().startswith("new"):
                docs.append("Business plan / project proposal")
            data["document_checklist"] = docs

        # If the LLM returned no matched schemes, fall back to the actual
        # retrieved citation ids so the Results page is never empty.
        if not data.get("matched_schemes"):
            data["matched_schemes"] = []
            for c in (citations or []):
                base = str(c).split("#")[0]
                if base and all(s.get("name") != base for s in data["matched_schemes"]):
                    data["matched_schemes"].append({
                        "name": base,
                        "why": "This scheme was retrieved for your goal; see the chat answer and official portal for details.",
                        "citations": [c],
                    })
            if not data.get("top_match") and data["matched_schemes"]:
                data["top_match"] = data["matched_schemes"][0]["name"]

        if not data.get("next_steps"):
            data["next_steps"] = [
                "Gather your documents",
                "Ask the assistant or visit the bank/department to confirm eligibility",
                "Apply through the official portal",
            ]
        if not data.get("recommendation_summary"):
            data["recommendation_summary"] = (
                "See the schemes below; the assistant explained how each may fit your goal. "
                "Please confirm final eligibility with the concerned bank/department."
            )
        dash = data.setdefault("dashboard", {})
        if (profile or {}).get("category") and not dash.get("category"):
            dash["category"] = profile["category"]
        if (profile or {}).get("loan_amount") and not dash.get("goal"):
            dash["goal"] = "Business funding goal (see profile)"
        return data

    async def _persist(self, result: Dict[str, Any]) -> None:
        """Best-effort save to the user_sessions table (service role)."""
        try:
            client = db.get_client(admin=True)
            client.table("user_sessions").upsert(
                {
                    "user_id": result.get("user_id"),
                    "user_email": result.get("user_email"),
                    "query": result.get("query"),
                    "profile": result.get("profile") or {},
                    "generated": result.get("generated") or {},
                },
                on_conflict="query",
            ).execute()
            logger.info("Persisted generated session (best-effort)")
        except Exception as e:
            # Table may not exist yet (DDL owner: user). Generation still works.
            logger.warning("Could not persist generated session (user_sessions table missing?): %s", e)


generate_service = GenerateService()
