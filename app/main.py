# Copyright 2024
# Directory: yt-rag/app/main.py

"""
FastAPI application for RAG (Retrieval-Augmented Generation) backend.
Provides endpoints for document seeding and question answering with citations.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response, JSONResponse

from .core.config import get_settings
from .core.database import db
from .models.requests import SeedRequest, AnswerRequest, FetchSchemeRequest, GenerateRequest
from .models.responses import (
    SeedResponse, AnswerResponse, HealthResponse, ErrorResponse,
    QuestionsResponse, FetchSchemeResponse, SchemesResponse, ToolsResponse,
)
from .services.rag import rag_service
from .services.history import history_service
from .services.generate import generate_service
from .services.questions import build_questions_payload
from .services.govt_source import govt_source_service, list_official_sources
from .services.tools import tools_as_json, gemini_function_declarations
from .data.default_documents import DEFAULT_DOCUMENTS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting RAG API application")
    
    try:
        # Initialize database connection
        await db.connect()
        
        # Check database schema
        await db.initialize_schema()
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down RAG API application")
    await db.disconnect()


# Create FastAPI application
app = FastAPI(
    title="Sahayak RAG Explainer Backend",
    description="RAG backend for Sahayak (SIH26092 - AI-Driven Scheme Matching for Marginalized Entrepreneurs). "
                 "Retrieves scheme source-document chunks via vector similarity search and generates a cited "
                 "'why this scheme' explanation. This service explains schemes; it does NOT decide eligibility "
                 "-- that is a separate deterministic rules engine per solution.md section 3.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # NextJS default
        "http://localhost:3001",  # Alternative port
        "https://yt-rag.vercel.app",  # Production frontend
        "*"  # Allow all for development (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for the chat interface
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Handle favicon requests to prevent 404 errors."""
    return Response(status_code=204)  # No Content


@app.get("/greet/{name}", tags=["General"])
async def greet(name: str):
    """
    Greet endpoint that returns a personalized greeting.
    
    Args:
        name (str): Name of the person to greet
        
    Returns:
        Personalized greeting message
    """
    return {"message": f"Hello, {name}! I think you are great!"}


@app.get("/healthz", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint with database connectivity test."""
    try:
        # Test database connection
        db_healthy = await db.health_check()
        
        return HealthResponse(
            status="ok" if db_healthy else "degraded",
            database_connected=db_healthy
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )


@app.get("/documents", tags=["General"])
async def get_documents():
    """
    Get the default documents used for seeding the knowledge base.
    
    Returns:
        List of default documents with their chunk_id, source, and text
    """
    return {"documents": DEFAULT_DOCUMENTS}


@app.post("/seed", response_model=SeedResponse, tags=["RAG"])
async def seed_documents(request: SeedRequest = SeedRequest()):
    """
    Seed the knowledge base with documents.
    
    If no documents are provided, seeds with default policy/FAQ documents.
    Documents are chunked, embedded, and stored in the vector database.
    """
    try:
        logger.info("Starting document seeding process")
        
        # Convert request documents to the format expected by RAG service
        documents = None
        if request.docs:
            documents = [
                {
                    'chunk_id': doc.chunk_id,
                    'source': doc.source,
                    'text': doc.text
                }
                for doc in request.docs
            ]
        
        # Process documents through RAG pipeline
        inserted_count = await rag_service.seed_documents(documents)
        
        logger.info(f"Seeding completed: {inserted_count} chunks inserted")
        
        return SeedResponse(inserted=inserted_count)
        
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to seed documents: {str(e)}"
        )


@app.post("/answer", response_model=AnswerResponse, tags=["RAG"])
async def answer_question(request: AnswerRequest):
    """
    Answer a question using RAG (Retrieval-Augmented Generation).

    Pipeline:
    1. Embed the query (optionally enriched with the applicant's profile)
    2. Vector similarity search to find relevant chunks
    3. Generate answer using LLM with context
    4. Return answer with citations and debug info

    Pass the applicant's prerequisite answers (from `/questions`) in `profile`
    so retrieval and the explanation match their situation. When
    `needs_prerequisites` is true in the response, ask the `/questions` list
    first and re-submit with a filled `profile`.
    """
    try:
        logger.info(f"Processing query: '{request.query[:100]}...'")

        # Convert pydantic profile to dict if provided
        profile = request.profile.dict(exclude_none=True) if request.profile else None

        # Process query through RAG pipeline
        result = await rag_service.answer_query(
            query=request.query,
            top_k=request.top_k,
            profile=profile,
        )

        # Convert to response model
        response = AnswerResponse(
            text=result['text'],
            citations=result['citations'],
            profile_used=result.get('profile_used'),
            needs_prerequisites=result.get('needs_prerequisites', False),
            debug={
                'top_doc_ids': result['debug']['top_doc_ids'],
                'latency_ms': result['debug']['latency_ms']
            }
        )

        # Log the Q&A for the monitoring dashboard (best-effort).
        await history_service.record(
            query=request.query,
            answer=response.text,
            citations=response.citations,
            profile=profile,
            user_id=request.user_id,
            user_email=request.user_email,
            needs_prerequisites=response.needs_prerequisites,
        )

        logger.info(f"Query processed successfully in {result['debug']['latency_ms']}ms")

        return response

    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {str(e)}"
        )


@app.get("/questions", response_model=QuestionsResponse, tags=["Prerequisites"])
async def get_prerequisite_questions():
    """
    Get the prerequisite (pre-requesting) questions.

    Ask these before calling `/answer` so the AI can narrow scheme retrieval
    to the applicant's profile (category, business stage, loan amount,
    business type, location). These questions do NOT determine eligibility --
    they only help the explainer give a better, cited answer.
    """
    return QuestionsResponse(**build_questions_payload())


@app.get("/schemes", response_model=SchemesResponse, tags=["Govt Sources"])
async def list_schemes():
    """
    List the official Indian government scheme portals this service can fetch
    and ingest (via `/fetch-scheme`). Prefer these over arbitrary web results.
    """
    return SchemesResponse(sources=list_official_sources())


@app.post("/fetch-scheme", response_model=FetchSchemeResponse, tags=["Govt Sources"])
async def fetch_scheme(request: FetchSchemeRequest):
    """
    Fetch a scheme description from an official government portal, chunk it,
    embed it, and store it in the Supabase vector DB so subsequent `/answer`
    queries can cite current live data.

    Useful for keeping the knowledge base fresh / extending it beyond the
    starter 4 schemes without hand-writing documents.
    """
    try:
        result = await govt_source_service.ingest_url(
            url=request.url,
            scheme=request.scheme,
            timeout=request.timeout,
        )
        return FetchSchemeResponse(**result)
    except Exception as e:
        logger.error(f"Fetch scheme failed: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch scheme from {request.url}: {str(e)}"
        )


@app.get("/tools", response_model=ToolsResponse, tags=["AI Tools"])
async def get_tools():
    """
    Return the AI function-calling (tool) definitions for this service.

    These JSON-Schema declarations describe how an LLM (e.g. Gemini within an
    agent loop) should call `/answer` (with a prerequisite profile) and
    `/fetch-scheme` (to pull current data from official govt portals). They map
    1:1 to the google-genai `FunctionDeclaration` objects used in `tools.py`.
    """
    return ToolsResponse(tools=tools_as_json())


@app.get("/api/history", tags=["Dashboard"])
async def get_history(limit: int = 50, user: str = None):
    """
    Return recent Q&A history for the monitoring dashboard.

    When a Supabase user email is supplied via ?user=, only that user's rows
    are returned (matches the frontend dashboard for a specific user). Without
    a user filter, returns the most recent rows across everyone (admin view).
    Uses the service-role key, so this endpoint must remain backend-only.
    """
    rows = await history_service.list_for_user(user_email=user, limit=limit)
    return {"history": rows, "count": len(rows)}


@app.get("/api/stats", tags=["Dashboard"])
async def get_stats():
    """Overall Q&A usage stats for the dashboard."""
    return await history_service.stats()


@app.post("/api/generate", tags=["AI Auto-Generation"])
async def generate_session(request: GenerateRequest):
    """
    Auto-generate the personalized Results / Dashboard / Documentation bundle
    for a completed chat session.

    Takes the user's final question, the RAG explainer's cited answer, and the
    applicant profile, then uses Groq to produce a structured recommendation,
    dashboard payload and documentation checklist. Returns the bundle so the
    frontend can render immediately; it is also saved (best-effort) to the
    `user_sessions` table so the pages can be refreshed later.

    Note: the generated output explains and cites — it never declares formal
    eligibility (that stays with the bank/department).
    """
    try:
        profile = request.profile.dict(exclude_none=True) if request.profile else None
        result = await generate_service.generate(
            query=request.query,
            answer=request.answer,
            citations=request.citations or [],
            profile=profile,
            user_id=request.user_id,
            user_email=request.user_email,
        )
        # Inject display name if the frontend supplied one.
        if request.full_name:
            gen = result.get("generated", {})
            dash = gen.get("dashboard", {})
            dash["full_name"] = request.full_name
            gen["dashboard"] = dash
            result["generated"] = gen
        return {
            "query": result["query"],
            "profile": result["profile"],
            "generated": result["generated"],
            "user_id": result["user_id"],
            "user_email": result["user_email"],
        }
    except Exception as e:
        logger.error(f"Auto-generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate session: {str(e)}")


@app.get("/tools/gemini", tags=["AI Tools"])
async def get_gemini_tools():
    """
    Return the same tool definitions serialized for direct use as Gemini
    `types.FunctionDeclaration` objects (as plain JSON Schema).
    """
    return {"schema_version": "google-genai", "tools": tools_as_json()}


# ─────────────────────────────────────────────────────────────────────────
# SAHAYAK WEBSITE PAGES (served from static/site/)
# Clean-URL routes are registered FIRST (so they win over the static mount),
# then static/site/ is mounted at the root so all relative asset references
# (style.css, app.js, images/...) resolve correctly.
# ─────────────────────────────────────────────────────────────────────────
_SITE_PAGES = {
    "": "index.html",
    "home": "index.html",
    "chat": "chat.html",
    "login": "login.html",
    "signup": "login.html",
    "dashboard": "dashboard.html",
    "results": "results.html",
    "scheme": "scheme.html",
    "documents": "documents.html",
    "documentation": "documentation.html",
}


@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse("static/site/index.html")


for _clean, _file in _SITE_PAGES.items():
    if _clean == "":
        continue

    @app.get("/" + _clean, include_in_schema=False)
    async def serve_page(_file=_file):
        return FileResponse("static/site/" + _file)


# Root static mount (registered AFTER the API + clean-URL routes so those
# always take precedence). Serves /style.css, /app.js, /images/..., etc.
app.mount("/", StaticFiles(directory="static/site", html=True), name="site")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "detail": "The requested endpoint does not exist",
            "available_endpoints": ["/", "/healthz", "/seed", "/answer", "/questions", "/fetch-scheme", "/tools", "/docs"]
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail="An unexpected error occurred. Please check the logs."
        ).model_dump()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
