# Copyright 2024
# Directory: yt-rag/app/services/govt_source.py

"""
Fetch and ingest scheme information from official Indian government portals.

This lets the AI / helper pull *current* scheme text from an official source
(e.g. standupmitra.in, kviconline.gov.in/pmegp, mudra.org.in, nsfdc.nic.in),
chunk it, embed it, and store it in the Supabase vector DB so subsequent
/answer queries can cite it. It is a best-effort ingestor: govt pages change
structure often, so it strips boilerplate and fails cleanly if a page can't
be parsed.

NOTE: This only *explains and stores what the portal says*. It never decides
eligibility -- the deterministic rules engine downstream is the source of
truth. Amounts on official portals may lag budget announcements; always
re-verify against the live portal before a real demo.
"""

import logging
import re
import hashlib
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup

from ..core.database import db
from ..services.embedding import embedding_service
from ..services.chunker import chunker

logger = logging.getLogger(__name__)

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/122.0 Safari/537.36")

# A small allow-list of known official scheme portals. AI/helpers should prefer
# these sources over arbitrary web results.
OFFICIAL_SCHEME_SOURCES: List[Dict[str, str]] = [
    {
        "scheme": "Stand-Up India",
        "url": "https://www.standupmitra.in",
        "portal": "StandUp Mitra (Ministry of Finance / DFS, via SIDBI)",
    },
    {
        "scheme": "PMEGP",
        "url": "https://www.kviconline.gov.in/pmegp",
        "portal": "PMEGP e-Portal (KVIC, Ministry of MSME)",
    },
    {
        "scheme": "MUDRA (PMMY)",
        "url": "https://www.mudra.org.in",
        "portal": "MUDRA (Ministry of Finance)",
    },
    {
        "scheme": "NSFDC",
        "url": "https://nsfdc.nic.in",
        "portal": "NSFDC (Ministry of Social Justice & Empowerment)",
    },
    {
        "scheme": "PM Vishwakarma",
        "url": "https://pmvishwakarma.gov.in",
        "portal": "PM Vishwakarma (Ministry of MSME)",
    },
]


def list_official_sources() -> List[Dict[str, str]]:
    """Return the known official govt scheme portals."""
    return OFFICIAL_SCHEME_SOURCES


def _extract_main_text(html: str) -> str:
    """Extract the main readable text from an official portal page."""
    soup = BeautifulSoup(html, "lxml")

    # Drop script/style/nav/footer noise
    for tag in soup(["script", "style", "noscript", "header", "footer",
                     "nav", "aside", "iframe", "form", "button", "svg"]):
        tag.decompose()

    # Prefer <main> or <article> if present, else body
    main = soup.find("main") or soup.find("article") or soup.body or soup

    text = main.get_text(separator="\n")
    text = re.sub(r'[\t ]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n', text)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    # Drop obviously short boilerplate lines to reduce noise
    meaningful = [ln for ln in lines if len(ln) > 20]
    return "\n".join(meaningful) if meaningful else "\n".join(lines)


def _chunk_id_from_url(url: str, scheme: str) -> str:
    """Stable deterministic chunk_id from a scheme + url."""
    slug = hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]
    safe_scheme = re.sub(r'[^a-zA-Z0-9]+', '_', scheme.lower()).strip('_')
    return f"{safe_scheme or 'scheme'}_{slug}"


class GovtSourceService:
    """Fetch, extract, embed and store official govt scheme pages."""

    async def fetch_text(self, url: str, timeout: int = 30) -> str:
        """Fetch and extract readable text from a govt portal URL."""
        # Many official .gov.in / scheme portals serve incomplete TLS chains, so
        # retry without strict verification when the verified request fails.
        try:
            resp = requests.get(
                url,
                headers={"User-Agent": USER_AGENT},
                timeout=timeout,
                allow_redirects=True,
            )
        except requests.exceptions.SSLError:
            logger.warning(f"SSL verification failed for {url}; retrying with verification disabled")
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            resp = requests.get(
                url,
                headers={"User-Agent": USER_AGENT},
                timeout=timeout,
                allow_redirects=True,
                verify=False,
            )
        resp.raise_for_status()
        return _extract_main_text(resp.text)

    async def ingest_url(
        self,
        url: str,
        scheme: Optional[str] = None,
        chunk_id_prefix: Optional[str] = None,
        timeout: int = 30,
    ) -> Dict[str, object]:
        """
        Fetch a govt page, chunk it, embed it and store in the vector DB.

        Returns a summary dict with extracted stats.
        """
        text = await self.fetch_text(url, timeout=timeout)
        if not text:
            raise ValueError(f"No readable text extracted from {url}")

        prefix = chunk_id_prefix or _chunk_id_from_url(url, scheme or "scheme")

        chunks = chunker.chunk_text(text, url, prefix)
        if not chunks:
            raise ValueError(f"Page at {url} produced no chunks")

        texts = [c["text"] for c in chunks]
        embeddings = await embedding_service.embed_texts(texts)
        for chunk, emb in zip(chunks, embeddings):
            chunk["embedding"] = emb

        inserted = await db.upsert_chunks(chunks)

        return {
            "url": url,
            "scheme": scheme,
            "chunks_created": len(chunks),
            "chunks_inserted": inserted,
            "chunk_id_prefix": prefix,
            "source_verified_fetch": True,
        }


# Global service instance
govt_source_service = GovtSourceService()
