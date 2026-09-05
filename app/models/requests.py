# Copyright 2024
# Directory: yt-rag/app/models/requests.py

"""
Request models for the RAG API endpoints.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """Individual document chunk for seeding."""
    chunk_id: str = Field(..., description="Unique identifier for the chunk",
                          examples=["scheme_pmegp_v1"])
    source: str = Field(..., description="Source URL or identifier",
                        examples=["https://www.kviconline.gov.in/pmegp"])
    text: str = Field(..., description="Text content of the chunk")


class SeedRequest(BaseModel):
    """Request model for the /seed endpoint."""
    docs: Optional[List[DocumentChunk]] = Field(
        None,
        description="Optional list of documents to seed. If omitted, uses default documents."
    )


class ApplicantProfile(BaseModel):
    """Prerequisite answers from the applicant, used to narrow scheme retrieval."""
    category: Optional[str] = Field(
        None, description="Category (SC/ST/OBC/Minority/Woman/PwD/Transgender/General/Other)",
        examples=["SC"])
    business_stage: Optional[str] = Field(
        None, description="Business stage", examples=["New / first venture"])
    business_type: Optional[str] = Field(
        None, description="Business type", examples=["Manufacturing"])
    loan_amount: Optional[str] = Field(
        None, description="Approx loan amount needed", examples=["5 lakh to 10 lakh"])
    location: Optional[str] = Field(
        None, description="Unit location", examples=["Rural"])
    extra: Optional[Dict[str, str]] = Field(
        None, description="Any additional profile fields", examples=None)


class AnswerRequest(BaseModel):
    """Request model for the /answer endpoint."""
    query: str = Field(
        ...,
        description="User question to answer",
        examples=["मुझे सिलाई मशीन खरीदने के लिए 2 लाख रुपये चाहिए, कौन सी योजना मदद करेगी?"],
    )
    profile: Optional[ApplicantProfile] = Field(
        None,
        description="Prerequisite answers (from /questions) used to narrow scheme retrieval. "
                    "Recommended so the explanation matches the applicant's situation.",
    )
    top_k: Optional[int] = Field(
        6,
        ge=1,
        le=20,
        description="Number of chunks to retrieve for context",
        examples=[6],
    )
    user_id: Optional[str] = Field(
        None,
        description="Supabase auth user id (for dashboard Q&A logging).",
    )
    user_email: Optional[str] = Field(
        None,
        description="Email of the logged-in user (for dashboard Q&A logging).",
    )


class FetchSchemeRequest(BaseModel):
    """Request model for the /fetch-scheme endpoint (fetch official govt page)."""
    url: str = Field(
        ...,
        description="Official government portal URL to fetch and ingest.",
        examples=["https://www.kviconline.gov.in/pmegp"],
    )
    scheme: Optional[str] = Field(
        None,
        description="Human-readable scheme name (used for the chunk_id).",
        examples=["PMEGP"],
    )
    timeout: Optional[int] = Field(
        30, ge=5, le=120, description="Fetch timeout in seconds", examples=[30])


class GenerateRequest(BaseModel):
    """Request model for the auto-generation endpoint.

    Takes a completed chat exchange (the final question + the RAG explainer's
    cited answer + the applicant profile) and returns an AI-generated bundle
    for the personalized Results, Dashboard and Documentation pages.
    """
    query: str = Field(..., description="The user's final question in the chat session.")
    answer: str = Field(..., description="The cited answer returned by /answer.")
    citations: Optional[List[str]] = Field(None, description="Cited chunk ids from /answer.")
    profile: Optional[ApplicantProfile] = Field(
        None, description="The applicant profile used during the chat.")
    user_id: Optional[str] = Field(None, description="Supabase auth user id.")
    user_email: Optional[str] = Field(None, description="Email of the logged-in user.")
    full_name: Optional[str] = Field(None, description="User's display name.")
