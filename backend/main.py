"""
backend/main.py
----------------
FastAPI application factory.
Registers all routers, configures CORS, and adds global exception handling.

Run with:
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.core.config import settings
from backend.api.routes import research, pdf, history
from backend.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 AI Research Agent API starting up…")
    logger.info(f"   Default LLM provider : {settings.default_llm_provider}")
    logger.info(f"   Groq model           : {settings.groq_model}")
    logger.info(f"   Gemini model         : {settings.gemini_model}")
    logger.info(f"   Exa configured       : {bool(settings.exa_api_key)}")
    yield
    logger.info("👋 API shutting down.")


app = FastAPI(
    title="AI Research Agent API",
    description=(
        "Production-ready research agent powered by "
        "Exa search + Groq/Gemini LLMs + LangGraph + ChromaDB RAG."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(research.router)
app.include_router(pdf.router)
app.include_router(history.router)


# ── Global exception handler ───────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {exc}"},
    )


@app.get("/", tags=["root"])
async def root():
    return {
        "name": "AI Research Agent API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/status",
    }
