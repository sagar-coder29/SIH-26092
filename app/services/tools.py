# Copyright 2024
# Directory: yt-rag/app/services/tools.py

"""
AI function-calling (tool) definitions for the Sahayak RAG service.

These are JSON-Schema-style `FunctionDeclaration`s that can be passed to a
Gemini model (google-genai `types.FunctionDeclaration`) so the model knows
how to call this service:

  - `sahayak_answer`: retrieve scheme matches + generate a cited explanation.
    Accepts the applicant's prerequisite answers via the `profile` object.
  - `fetch_official_scheme`: fetch and ingest a currently-live scheme page from
    an official govt portal into the vector DB (so answers use fresh data).

Keeping these as Plain-Old-Python-Callables in a single module makes the same
definitions available as (a) JSON docs in /docs, (b) Gemini `tools`, and
(c) reference for the React frontend.
"""

from typing import List, Dict, Any


def _to_dict_tools() -> List[Dict[str, Any]]:
    """Return function callable declarations as plain dicts (JSON-ready)."""
    return [
        {
            "name": "sahayak_answer",
            "description": (
                "Retrieve the most relevant Indian government schemes for a "
                "marginalized entrepreneur's business goal and generate a cited "
                "'why this scheme' explanation. Use the applicant's prerequisite "
                "answers (profile) to narrow the search. This service explains "
                "schemes only; it does NOT return an eligibility verdict."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The applicant's business goal or question, in Hindi/English/Hinglish.",
                    },
                    "profile": {
                        "type": "object",
                        "description": "Answers to the prerequisite questions (from /questions).",
                        "properties": {
                            "category": {"type": "string", "enum": ["SC", "ST", "OBC", "Minority", "Woman", "PwD", "Transgender", "General/Other"]},
                            "business_stage": {"type": "string", "enum": ["New / first venture", "Expanding existing business", "Existing business (not expansion)"]},
                            "business_type": {"type": "string", "enum": ["Manufacturing", "Services", "Trading", "Agriculture / agri-allied"]},
                            "loan_amount": {"type": "string"},
                            "location": {"type": "string", "enum": ["Rural", "Urban"]},
                        },
                        "required": ["business_stage", "category", "loan_amount"],
                    },
                    "top_k": {"type": "integer", "minimum": 1, "maximum": 20, "default": 6},
                },
                "required": ["query"],
            },
        },
        {
            "name": "fetch_official_scheme",
            "description": (
                "Fetch and ingest a scheme description from an official Indian "
                "government portal into the vector database, so later answers can "
                "cite current, live scheme data. Prefer sources from the official "
                "allow-list (/schemes)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Official govt portal URL to fetch (e.g. standupmitra.in, kviconline.gov.in/pmegp).",
                    },
                    "scheme": {
                        "type": "string",
                        "description": "Human-readable scheme name, e.g. 'PMEGP'.",
                    },
                },
                "required": ["url"],
            },
        },
    ]


def gemini_function_declarations() -> List[Any]:
    """
    Return tool definitions as google-genai FunctionDeclaration objects,
    ready to pass to Gemini via `types.Tool(function_declarations=[...])`.
    """
    try:
        from google.genai import types
        decls = []
        for t in _to_dict_tools():
            decls.append(types.FunctionDeclaration(
                name=t["name"],
                description=t["description"],
                parameters=types.Schema(**t["parameters"]),
            ))
        return decls
    except Exception as e:  # pragma: no cover - only if google-genai absent
        logger = __import__("logging").getLogger(__name__)
        logger.warning(f"Could not build Gemini FunctionDeclarations: {e}")
        return _to_dict_tools()


def tools_as_json() -> List[Dict[str, Any]]:
    """Return tool definitions as JSON-ready dicts (for /tools and /docs)."""
    return _to_dict_tools()
