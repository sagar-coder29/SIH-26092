# Copyright 2024
# Directory: yt-rag/app/models/responses.py

"""
Response models for the RAG API endpoints.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SeedResponse(BaseModel):
    """Response model for the /seed endpoint."""
    inserted: int = Field(..., description="Number of chunks successfully inserted",
                          examples=[4])


class DebugInfo(BaseModel):
    """Debug information for RAG responses."""
    top_doc_ids: List[str] = Field(..., description="IDs of retrieved chunks",
                                   examples=[["scheme_pmegp_v1#1", "scheme_mudra_pmmy_v1#1"]])
    latency_ms: int = Field(..., description="Total processing time in milliseconds",
                            examples=[980])


class AnswerResponse(BaseModel):
    """Response model for the /answer endpoint."""
    text: str = Field(..., description="Generated answer with inline citations")
    citations: List[str] = Field(..., description="List of chunk IDs used as sources",
                                 examples=[["scheme_pmegp_v1#1"]])
    offline_access: Optional[List[str]] = Field(
        None, description="Physical bank branches and government offices where the "
                          "scheme can be availed in person (offline access points)")
    debug: DebugInfo = Field(..., description="Debug information")
    profile_used: Optional[Dict[str, Any]] = Field(
        None, description="The prerequisite profile that was used (if provided)")
    needs_prerequisites: Optional[bool] = Field(
        None, description="True if prerequisites were missing and should be collected first")


class PrerequisiteQuestion(BaseModel):
    """A single prerequisite question."""
    key: str = Field(..., description="Stable key for the question", examples=["category"])
    question: str = Field(..., description="The question text (Hindi + English)")
    type: str = Field(..., description="Question type (choice/text)", examples=["choice"])
    options: Optional[List[str]] = Field(None, description="Choices for choice-type questions")
    optional: bool = Field(..., description="Whether answering is optional")


class QuestionsResponse(BaseModel):
    """Response model for the /questions endpoint."""
    version: str = Field(..., description="Question set version", examples=["1.0"])
    intro: str = Field(..., description="Intro/explainer shown before the questions")
    questions: List[PrerequisiteQuestion] = Field(..., description="The prerequisite questions")


class FetchSchemeResponse(BaseModel):
    """Response model for the /fetch-scheme endpoint."""
    url: str = Field(..., description="Fetched URL")
    scheme: Optional[str] = Field(None, description="Scheme name")
    chunks_created: int = Field(..., description="Chunks extracted from the page", examples=[6])
    chunks_inserted: int = Field(..., description="Chunks stored in the vector DB", examples=[6])
    chunk_id_prefix: str = Field(..., description="Prefix used for the stored chunk IDs")
    source_verified_fetch: bool = Field(..., description="True if page fetched successfully")


class OfficialSource(BaseModel):
    """An official govt scheme portal that can be fetched."""
    scheme: str = Field(..., description="Scheme name")
    url: str = Field(..., description="Official portal URL")
    portal: str = Field(..., description="Implementing body / ministry")


class SchemesResponse(BaseModel):
    """Response model for the /schemes endpoint (list of official sources)."""
    sources: List[OfficialSource] = Field(..., description="Official govt scheme sources")


class ToolsResponse(BaseModel):
    """Response model for the /tools endpoint (AI function-calling definitions)."""
    tools: List[Dict[str, Any]] = Field(
        ..., description="Function-calling tool definitions usable by an AI model")


class HealthResponse(BaseModel):
    """Response model for the /healthz endpoint."""
    status: str = Field(..., description="Health status", examples=["ok"])
    database_connected: bool = Field(..., description="Database connection status", examples=[True])


class EMIResult(BaseModel):
    """Response model for the /api/emi endpoint (EMI calculator)."""
    principal: float = Field(..., description="Loan amount in INR", examples=[500000])
    annual_rate: float = Field(..., description="Annual interest rate in percent", examples=[8.5])
    tenure_months: int = Field(..., description="Loan tenure in months", examples=[60])
    monthly_rate: float = Field(..., description="Monthly interest rate in percent", examples=[0.7083])
    emi: float = Field(..., description="Monthly instalment in INR", examples=[10256.62])
    total_interest: float = Field(..., description="Total interest paid over the loan", examples=[115397.2])
    total_payment: float = Field(..., description="Total paid (principal + interest)", examples=[615397.2])
    processing_fee_percent: float = Field(0.0, description="Processing fee as percent of principal")
    processing_fee: float = Field(0.0, description="Processing fee amount in INR", examples=[5000])
    net_disbursal: float = Field(..., description="Principal minus processing fee", examples=[495000])
    effective_annual_rate: float = Field(..., description="Approx effective APR on net disbursal", examples=[8.68])
    schedule: Optional[List[Dict[str, Any]]] = Field(
        None, description="Month-by-month amortization schedule (month, emi, interest, principal, balance)")


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="Error message")
    detail: str = Field(..., description="Detailed error information")
