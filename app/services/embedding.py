# Copyright 2024
# Directory: yt-rag/app/services/embedding.py

"""
Embedding service for generating text embeddings.
Supports Gemini (gemini-embedding-001, default) and OpenAI, controlled by
EMBEDDING_PROVIDER in .env. Gemini's embedding model was picked as the
default for Sahayak because it natively supports Hindi (and 100+ other
languages) alongside English, which matters since users describe their
business goal "मैं सिलाई का काम करता हूँ..." in either language.
"""

import logging
from typing import List
import openai
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingService:
    """Service for generating text embeddings using OpenAI or Gemini."""

    def __init__(self):
        """Initialize the embedding client based on EMBEDDING_PROVIDER."""
        self.provider = settings.embedding_provider

        if self.provider == "openai":
            self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
            self.embed_model = settings.openai_embed_model

        elif self.provider == "gemini":
            # Lazy import so `openai`-only setups don't need google-genai installed.
            from google import genai
            self.gemini_client = genai.Client(api_key=settings.gemini_api_key)
            self.embed_model = settings.gemini_embed_model

        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}")

        logger.info(f"Initialized embedding service with {self.provider} ({self.embed_model})")

    async def embed_texts(self, texts: List[str], task_type: str = "RETRIEVAL_DOCUMENT") -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed
            task_type: Gemini-only hint ("RETRIEVAL_DOCUMENT" when embedding
                       chunks to store, "RETRIEVAL_QUERY" when embedding a
                       user question). Ignored for OpenAI.

        Returns:
            List of embedding vectors (length = settings.embedding_dimensions)
        """
        try:
            if self.provider == "openai":
                response = self.openai_client.embeddings.create(
                    model=self.embed_model,
                    input=texts
                )
                embeddings = [item.embedding for item in response.data]

            else:  # gemini
                from google.genai import types
                result = self.gemini_client.models.embed_content(
                    model=self.embed_model,
                    contents=texts,
                    config=types.EmbedContentConfig(
                        task_type=task_type,
                        output_dimensionality=settings.embedding_dimensions,
                    ),
                )
                embeddings = [e.values for e in result.embeddings]

            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings

        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise

    async def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query.

        NOTE: We use task_type="RETRIEVAL_DOCUMENT" (the SAME task type used
        when embedding chunks for storage) so the query vector and the stored
        document vectors live in the SAME embedding space. Using
        "RETRIEVAL_QUERY" here put the query in a different subspace and
        caused vector-search matches to return nothing (cosine similarity near
        0). Keeping the task type consistent guarantees comparable vectors.

        Args:
            query: Query text to embed

        Returns:
            Embedding vector
        """
        embeddings = await self.embed_texts([query], task_type="RETRIEVAL_DOCUMENT")
        return embeddings[0]


# Global service instance
embedding_service = EmbeddingService()
