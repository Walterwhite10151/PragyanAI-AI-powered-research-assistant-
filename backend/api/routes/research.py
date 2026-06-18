"""
backend/api/routes/research.py
--------------------------------
POST /api/research  — Run the full research pipeline.
GET  /api/status    — Health check + provider info.

CHANGES vs. the original version:
  Added explicit except clauses for the typed Exa errors (raised by
  backend/tools/exa_search.py) BEFORE the generic `except Exception`.
  Previously every Exa failure — rate limits, bad requests, auth issues,
  upstream outages — was indistinguishable from a real server bug and
  got reported to the client as a flat 500. Now:
    429 (rate limit)      -> HTTP 429
    400/412/422 (bad req) -> HTTP 400
    401/403 (auth/config) -> HTTP 503 (message doesn't leak key details)
    everything else Exa-specific -> HTTP 502 (clearly an upstream issue)
    anything unrelated to Exa -> still HTTP 500, unchanged
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.api.schemas import (
    ResearchRequest, ResearchResponse,
    SourceItem, VideoItem, StatusResponse, ProviderInfo,
)
from backend.services.research_agent import run_research
from backend.services.llm_service import list_available_providers
from backend.rag.vector_store import get_vector_store
from backend.tools.exa_search import (
    ExaSearchError,
    ExaRateLimitError,
    ExaAuthError,
    ExaInvalidRequestError,
)
from backend.utils.storage import save_session
from backend.utils.logger import logger
from backend.core.config import settings

router = APIRouter(prefix="/api", tags=["research"])


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Health check and provider configuration status."""
    vs = get_vector_store()
    providers = [ProviderInfo(**p) for p in list_available_providers()]
    return StatusResponse(
        status="ok",
        providers=providers,
        vector_store_chunks=vs.doc_count,
        exa_configured=bool(settings.exa_api_key),
    )


@router.post("/research", response_model=ResearchResponse)
async def research(req: ResearchRequest):
    """
    Run the full 8-node LangGraph research pipeline.

    Steps internally:
      Exa search → RAG retrieve → Overview → Key Concepts
      → Facts → Roadmap → Summary → YouTube
    """
    logger.info(f"Research request: topic={req.topic!r}, provider={req.provider}")

    try:
        state = run_research(topic=req.topic, provider=req.provider)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ExaRateLimitError as exc:
        logger.warning(f"Exa rate limit during research: {exc}")
        raise HTTPException(
            status_code=429,
            detail="Search provider rate limit reached. Please try again in a moment.",
        )
    except ExaAuthError as exc:
        logger.error(f"Exa auth/config error during research: {exc}")
        raise HTTPException(
            status_code=503,
            detail="Search provider is misconfigured. Contact the site administrator.",
        )
    except ExaInvalidRequestError as exc:
        logger.error(f"Exa rejected the request during research: {exc}")
        raise HTTPException(status_code=400, detail=str(exc))
    except ExaSearchError as exc:
        # Catches ExaNotFoundError / ExaServiceError — anything Exa-side
        # that isn't one of the more specific cases above.
        logger.error(f"Exa search failed during research: {exc}")
        raise HTTPException(
            status_code=502,
            detail="The search provider is temporarily unavailable. Please try again shortly.",
        )
    except Exception as exc:
        logger.exception("Research pipeline error")
        raise HTTPException(status_code=500, detail=f"Research failed: {exc}")

    # Serialise Exa results → SourceItem
    sources = [
        SourceItem(
            title=r.title,
            url=r.url,
            snippet=r.snippet,
            published_date=r.published_date,
            score=r.score,
        )
        for r in state.get("exa_results", [])
    ]

    # Serialise YouTube results → VideoItem
    videos = [
        VideoItem(
            title=v.title,
            channel=v.channel,
            url=v.url,
            thumbnail=v.thumbnail,
            duration=v.duration,
            views=v.views,
        )
        for v in state.get("youtube_videos", [])
    ]

    # Persist session
    session_id = save_session(
        topic=req.topic,
        provider=req.provider,
        result={
            "overview": state["overview"],
            "key_concepts": state["key_concepts"],
            "important_facts": state["important_facts"],
            "roadmap": state["roadmap"],
            "summary": state["summary"],
            "sources": [s.model_dump() for s in sources],
        },
    )

    return ResearchResponse(
        topic=req.topic,
        provider=req.provider,
        overview=state["overview"],
        key_concepts=state["key_concepts"],
        important_facts=state["important_facts"],
        roadmap=state["roadmap"],
        summary=state["summary"],
        sources=sources,
        youtube_videos=videos,
        errors=state["errors"],
        elapsed_seconds=state["elapsed_seconds"],
        session_id=session_id,
    )