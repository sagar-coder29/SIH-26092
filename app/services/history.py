# Copyright 2024
# Directory: yt-rag/app/services/history.py

"""
Q&A history logging helper for the Sahayak monitoring dashboard.

Each /answer call is recorded into Supabase `chat_history` so the website's
Dashboard page can show a per-user log of every question they asked and the
cited answer the RAG explainer returned. Uses the service-role (admin)
client so it works for both anonymous and authenticated browsers.
"""

import logging
from typing import Any, Dict, Optional
from ..core.database import db

logger = logging.getLogger(__name__)


class HistoryService:
    """Record and retrieve Q&A history from Supabase."""

    async def record(
        self,
        query: str,
        answer: str,
        citations: Optional[list] = None,
        profile: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        needs_prerequisites: bool = False,
    ) -> Optional[int]:
        """Insert a Q&A row; returns the new id or None on failure."""
        try:
            client = db.get_client(admin=True)
            result = client.table("chat_history").insert({
                "user_id": user_id,
                "user_email": user_email,
                "query": query,
                "answer": answer,
                "citations": citations or [],
                "profile": profile or {},
                "needs_prerequisites": needs_prerequisites,
            }).execute()
            rows = result.data or []
            row_id = rows[0]["id"] if rows else None
            logger.info(f"Recorded chat history id={row_id} user={user_email or 'anonymous'}")
            return row_id
        except Exception as e:
            # Never break an answer because history logging failed.
            logger.warning(f"Failed to record chat history: {e}")
            return None

    async def list_for_user(self, user_id: Optional[str] = None,
                            user_email: Optional[str] = None, limit: int = 50) -> list:
        """Return the most recent history rows for a user (or all if no user)."""
        try:
            client = db.get_client(admin=True)
            query = client.table("chat_history").select("*").order("created_at", desc=True).limit(limit)
            if user_id:
                query = query.eq("user_id", user_id)
            elif user_email:
                query = query.eq("user_email", user_email)
            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to load chat history: {e}")
            return []

    async def stats(self) -> Dict[str, Any]:
        """Simple dashboard stats across all history."""
        try:
            client = db.get_client(admin=True)
            rows = client.table("chat_history").select("user_email").execute().data or []
            return {
                "total_queries": len(rows),
                "unique_users": len({r.get("user_email") or "anonymous" for r in rows}),
            }
        except Exception as e:
            logger.error(f"Failed to load chat stats: {e}")
            return {"total_queries": 0, "unique_users": 0}


history_service = HistoryService()