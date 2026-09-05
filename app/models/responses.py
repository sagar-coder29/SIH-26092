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


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="Error message")
    detail: str = Field(..., description="Detailed error information")
