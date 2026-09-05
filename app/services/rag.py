# Copyright 2024
# Directory: yt-rag/app/services/rag.py

"""
RAG (Retrieval-Augmented Generation) service implementation.
Orchestrates the complete RAG pipeline: chunk → embed → search → generate.
"""

import logging
import time
import re
from typing import List, Dict, Any, Tuple
from ..core.database import db
from .embedding import embedding_service
from .chat import chat_service
from .chunker import chunker
from ..data.default_documents import DEFAULT_DOCUMENTS

logger = logging.getLogger(__name__)


class RAGService:
    """Main RAG service orchestrating the complete pipeline."""
    
    def __init__(self):
        """Initialize RAG service."""
        self.db = db
        self.embedding_service = embedding_service
        self.chat_service = chat_service
        self.chunker = chunker
    
    async def seed_documents(self, documents: List[Dict[str, str]] = None) -> int:
        """
        Seed the knowledge base with documents.
        
        Args:
            documents: Optional list of documents. If None, uses default documents.
            
        Returns:
            Number of chunks successfully inserted
        """
        start_time = time.time()
        
        # Use default documents if none provided
        if documents is None:
            documents = DEFAULT_DOCUMENTS
            logger.info("Using default documents for seeding")
        
        try:
            # Step 1: Chunk documents
            chunks = self.chunker.chunk_documents(documents)
            logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
            
            # Step 2: Generate embeddings for all chunks
            texts = [chunk['text'] for chunk in chunks]
            embeddings = await self.embedding_service.embed_texts(texts)
            
            # Step 3: Combine chunks with embeddings
            for chunk, embedding in zip(chunks, embeddings):
                chunk['embedding'] = embedding
            
            # Step 4: Store in database
            inserted_count = await self.db.upsert_chunks(chunks)
            
            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.info(f"Seeding completed in {elapsed_ms}ms: {inserted_count} chunks inserted")
            
            return inserted_count
            
        except Exception as e:
            logger.error(f"Seeding failed: {e}")
            raise
    
    async def answer_query(self, query: str, top_k: int = 6,
                           profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a query through the complete RAG pipeline.

        Args:
            query: User's question
            top_k: Number of chunks to retrieve
            profile: Optional dict of prerequisite answers used to build a
                     richer, profile-aware query so retrieval matches the
                     applicant's situation (it also feeds the explanation).

        Returns:
            Dictionary with answer, citations, profile_used, needs_prerequisites,
            and debug info.
        """
        start_time = time.time()

        try:
            # Build a retrieval query from the user's question + profile facts.
            retrieval_query = self._build_retrieval_query(query, profile)

            # Step 1: Generate query embedding
            query_embedding = await self.embedding_service.embed_query(retrieval_query)

            # Step 2: Vector similarity search
            search_results = await self.db.vector_search(query_embedding, top_k)

            if not search_results:
                return {
                    'text': "I don't have enough information to answer your question. Could you please rephrase or provide more context?",
                    'citations': [],
                    'profile_used': profile,
                    'needs_prerequisites': False,
                    'debug': {
                        'top_doc_ids': [],
                        'latency_ms': int((time.time() - start_time) * 1000)
                    }
                }

            # Step 3: Deduplicate and prepare context
            context_blocks = self._prepare_context(search_results)

            # Step 4: Ask prerequisite questions up front if this looks like a
            # scheme-recommendation request and we have no profile yet.
            needs_prereq = self._should_ask_prerequisites(query, profile, context_blocks)

            # Pass profile context to the LLM so the explanation addresses it.
            answer_text = await self.chat_service.generate_answer(
                query, context_blocks, profile=profile)

            # Step 5: Extract citations from answer
            citations = self._extract_citations(answer_text, context_blocks)

            elapsed_ms = int((time.time() - start_time) * 1000)

            result = {
                'text': answer_text,
                'citations': citations,
                'profile_used': profile,
                'needs_prerequisites': needs_prereq,
                'debug': {
                    'top_doc_ids': [block['chunk_id'] for block in context_blocks],
                    'latency_ms': elapsed_ms
                }
            }

            logger.info(f"Query processed in {elapsed_ms}ms with {len(citations)} citations")
            return result

        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                'text': f"I encountered an error while processing your question: {str(e)}",
                'citations': [],
                'profile_used': profile,
                'needs_prerequisites': False,
                'debug': {
                    'top_doc_ids': [],
                    'latency_ms': int((time.time() - start_time) * 1000)
                }
            }

    def _build_retrieval_query(self, query: str, profile: Dict[str, Any]) -> str:
        """Combine the user question with profile facts for better retrieval."""
        parts = [query]
        if profile:
            for key, label in [
                ("business_stage", "business stage"),
                ("business_type", "business type"),
                ("category", "category"),
                ("loan_amount", "loan amount"),
                ("location", "location"),
            ]:
                val = profile.get(key)
                if val:
                    parts.append(f"{label}: {val}")
        return " ".join(parts)

    def _should_ask_prerequisites(self, query: str, profile: Dict[str, Any],
                                  context_blocks: List[Dict[str, Any]]) -> bool:
        """
        Heuristic: a scheme-recommendation question with no profile should
        prompt the client (via needs_prerequisites=True) to collect the
        prerequisite questions first.
        """
        if profile and any(profile.get(k) for k in ("business_stage", "category", "loan_amount")):
            return False
        scheme_markers = ("scheme", "yojana", "yojna", "loan", "subsidy", "स्कीम",
                          "योजना", "लोन", "सब्सिडी", "सिलाई", "business", "उद्यम")
        q = query.lower()
        if any(m in q for m in scheme_markers):
            return True
        return bool(context_blocks)
    
    def _prepare_context(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepare context blocks from search results with simple deduplication.
        
        Args:
            search_results: Raw search results from database
            
        Returns:
            Processed context blocks
        """
        # Simple deduplication by chunk_id prefix (MMR-lite)
        seen_prefixes = set()
        context_blocks = []
        
        for result in search_results:
            chunk_id = result.get('chunk_id', '')
            
            # Extract base chunk ID (before #)
            base_id = chunk_id.split('#')[0] if '#' in chunk_id else chunk_id
            
            if base_id not in seen_prefixes:
                context_blocks.append(result)
                seen_prefixes.add(base_id)
            
            # Limit to reasonable context size
            if len(context_blocks) >= 4:
                break
        
        logger.info(f"Prepared {len(context_blocks)} unique context blocks")
        return context_blocks
    
    def _extract_citations(self, answer_text: str, context_blocks: List[Dict[str, Any]]) -> List[str]:
        """
        Extract citation chunk_ids from the generated answer.

        Primary source: explicit [chunk_id] markers the LLM emitted in the text.
        Fallback: if no valid markers were found but the answer was built from
        retrieved context, return the top retrieved chunk_ids so the chat UI's
        "Sources" never renders empty for an answer that used the knowledge base.
        Matching is prefix-tolerant (accepts "scheme_pmegp_v1" even when the LLM
        drops the "#1" part or uses a slightly truncated id).

        Args:
            answer_text: Generated answer text
            context_blocks: Context blocks that were provided

        Returns:
            List of chunk_ids that were cited (or retrieved, as fallback)
        """
        # The full chunk_ids that were in the context (e.g. "scheme_pmegp_v1#1").
        ordered_blocks = [block['chunk_id'] for block in context_blocks]
        valid_chunk_ids = set(ordered_blocks)

        # Allow matching by base prefix too (id before "#"), so citations that
        # omit the chunk number still resolve to the actual retrieved chunk.
        base_lookup = {}
        for cid in ordered_blocks:
            base = cid.split('#')[0]
            base_lookup.setdefault(base, cid)

        # Find all citations in format [chunk_id]
        citation_pattern = r'\[([^\]]+)\]'
        found_citations = re.findall(citation_pattern, answer_text)

        # Resolve each found citation to a real context chunk_id, then dedupe
        # while preserving textual order.
        resolved = []
        for cite in found_citations:
            if cite in valid_chunk_ids:
                target = cite
            elif cite in base_lookup:
                target = base_lookup[cite]
            else:
                continue
            if target not in resolved:
                resolved.append(target)

        # Fallback: context was clearly used (we have blocks) but the LLM did
        # not emit any resolvable citation markers. Return the retrieved chunks
        # so the answer is always sourced.
        if not resolved and ordered_blocks:
            return list(dict.fromkeys(ordered_blocks))

        return resolved


# Global RAG service instance
rag_service = RAGService()
