# Copyright 2024
# Directory: yt-rag/app/core/config.py

"""
Configuration management for the RAG application.
Handles environment variables and application settings.

Modified for Sahayak (SIH26092 - AI-Driven Scheme Matching for
Marginalized Entrepreneurs). This RAG layer powers the "Explainer"
engine described in solution.md (Feature 3: Explainable Ranking +
Document Checklist) -- it retrieves scheme source documents and
generates a cited "why this scheme" explanation. It does NOT decide
eligibility; that is a separate deterministic rules engine per the
architecture in solution.md section 3.
"""

import os
from typing import Literal
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Supabase Configuration
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_anon_key: str = Field(..., env="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field(..., env="SUPABASE_SERVICE_ROLE_KEY")

    # AI Provider Configuration
    # "groq" is the default -- served via Groq's OpenAI-compatible API
    # (fast, no rate-limit outages like free Gemini). "gemini", "openai" and
    # "anthropic" are kept as drop-in alternatives.
    ai_provider: Literal["openai", "anthropic", "gemini", "groq"] = Field(default="groq", env="AI_PROVIDER")
    embedding_provider: Literal["openai", "gemini"] = Field(default="gemini", env="EMBEDDING_PROVIDER")

    # OpenAI Configuration
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_embed_model: str = Field(default="text-embedding-3-small", env="OPENAI_EMBED_MODEL")
    openai_chat_model: str = Field(default="gpt-4o", env="OPENAI_CHAT_MODEL")

    # Groq Configuration (OpenAI-compatible endpoint)
    groq_api_key: str = Field(default="", env="GROQ_API_KEY")
    groq_chat_model: str = Field(default="llama-3.3-70b-versatile", env="GROQ_CHAT_MODEL")
    groq_base_url: str = Field(default="https://api.groq.com/openai/v1", env="GROQ_BASE_URL")

    # Anthropic Configuration
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    anthropic_chat_model: str = Field(default="claude-3-5-sonnet-20241022", env="ANTHROPIC_CHAT_MODEL")

    # Gemini Configuration
    # Paste your Google AI Studio key into GEMINI_API_KEY if AI_PROVIDER=gemini.
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    gemini_chat_model: str = Field(default="gemini-2.5-flash", env="GEMINI_CHAT_MODEL")
    gemini_embed_model: str = Field(default="gemini-embedding-001", env="GEMINI_EMBED_MODEL")
    gemini_max_retries: int = Field(default=4, env="GEMINI_MAX_RETRIES")
    gemini_retry_delay: float = Field(default=7.0, env="GEMINI_RETRY_DELAY")

    # Application Configuration
    environment: str = Field(default="development", env="ENVIRONMENT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # RAG Configuration
    default_top_k: int = Field(default=6)
    chunk_size: int = Field(default=400)  # Approximate tokens
    chunk_overlap: int = Field(default=60)  # 15% overlap
    temperature: float = Field(default=0.1)

    # Vector dimensions MUST match sql/init_supabase.sql's VECTOR(...) column
    # and the embedding_provider above.
    #   - gemini-embedding-001 -> use 768 (default here; model supports
    #     768/1536/3072 via Matryoshka output_dimensionality, 768 keeps
    #     pgvector indexing cheap and is plenty for scheme-length docs)
    #   - OpenAI text-embedding-3-small -> 1536
    # If you change this, re-run sql/init_supabase.sql with matching
    # VECTOR(N) values before re-seeding, or old rows will mismatch.
    embedding_dimensions: int = Field(default=768, env="EMBEDDING_DIMENSIONS")

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance."""
    return settings
