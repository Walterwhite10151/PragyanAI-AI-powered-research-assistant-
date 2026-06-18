"""
backend/services/research_agent.py
------------------------------------
LangGraph StateGraph research pipeline.

Flow:
  exa_search → rag_retrieve → overview → key_concepts
    → facts → roadmap → summary → youtube → END

The LLM provider (Groq / Gemini) is injected per-run so the graph
handles both without recompilation.

CHANGE vs. the original version:
  Every LLM node used to call `get_llm(state["provider"])` *outside*
  the protected `_invoke()` try/except. If the provider name was wrong,
  the API key was missing/invalid, or the provider's SDK raised an
  auth/rate-limit error, that exception had nowhere to go — it propagated
  all the way up through run_research() and out as an unhandled 500 in
  research.py, regardless of how well-behaved exa_search_node was.
  `get_llm()` is now called *inside* `_invoke()`, so a provider failure
  degrades that one section into an `errors` entry (same pattern already
  used for exa_search_node, rag_retrieve_node, and youtube_node) instead
  of taking down the whole request.
"""

from __future__ import annotations

import time
from typing import Any, TypedDict, List, Optional

from langgraph.graph import StateGraph, END

from backend.services.research_chains import (
    overview_chain, key_concepts_chain, important_facts_chain,
    roadmap_chain, summary_chain,
)
from backend.services.llm_service import get_llm, LLMProvider
from backend.tools.exa_search import search_exa, format_results_for_llm, ExaResult
from backend.tools.youtube_search import search_youtube, VideoResult
from backend.rag.vector_store import get_vector_store
from backend.utils.logger import logger


# ── State ──────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    topic: str
    provider: str
    exa_results: List[ExaResult]
    search_text: str
    rag_context: str
    overview: str
    key_concepts: str
    important_facts: str
    roadmap: str
    summary: str
    youtube_videos: List[VideoResult]
    errors: List[str]
    elapsed_seconds: float


def _empty_state(topic: str, provider: str) -> AgentState:
    return AgentState(
        topic=topic, provider=provider,
        exa_results=[], search_text="", rag_context="",
        overview="", key_concepts="", important_facts="",
        roadmap="", summary="", youtube_videos=[],
        errors=[], elapsed_seconds=0.0,
    )


# ── Nodes ──────────────────────────────────────────────────────────────────────

def exa_search_node(state: AgentState) -> dict:
    logger.info(f"[Node] exa_search — {state['topic']!r}")
    try:
        results = search_exa(state["topic"])
        # Also index snippets into ChromaDB for cross-session RAG
        vs = get_vector_store()
        snippets = [r.content for r in results if r.content]
        vs.index_texts(snippets, source=f"exa:{state['topic'][:40]}")
        return {
            "exa_results": results,
            "search_text": format_results_for_llm(results),
        }
    except Exception as exc:
        logger.error(f"exa_search_node: {exc}")
        return {"errors": state["errors"] + [f"Exa search failed: {exc}"]}


def rag_retrieve_node(state: AgentState) -> dict:
    logger.info("[Node] rag_retrieve")
    try:
        vs = get_vector_store()
        chunks = vs.retrieve(state["topic"], top_k=5)
        ctx = "\n\n---\n\n".join(chunks) if chunks else "No prior documents indexed."
        return {"rag_context": ctx}
    except Exception as exc:
        logger.error(f"rag_retrieve_node: {exc}")
        return {"rag_context": "No context available.", "errors": state["errors"] + [str(exc)]}


_MAX_CONTEXT_CHARS = 2000   # search_results cap — keeps total prompt size well under the tightest TPM ceiling (6K on llama-3.1-8b-instant)
_MAX_RAG_CHARS = 800        # rag_context cap — deprioritised since it often duplicates search_results for fresh topics


def _invoke(chain_fn, provider: str, inputs: dict, state: AgentState, label: str) -> dict:
    """Shared helper: build the LLM, invoke the chain, and catch errors from
    EITHER step — a bad provider/API key now degrades the same way a bad
    chain response would, instead of crashing the whole request.

    search_results and rag_context are truncated here, once, for every
    chain that uses them — instead of each chain receiving the full
    untrimmed blob independently."""
    capped_inputs = dict(inputs)
    if "search_results" in capped_inputs and isinstance(capped_inputs["search_results"], str):
        capped_inputs["search_results"] = capped_inputs["search_results"][:_MAX_CONTEXT_CHARS]
    if "rag_context" in capped_inputs and isinstance(capped_inputs["rag_context"], str):
        capped_inputs["rag_context"] = capped_inputs["rag_context"][:_MAX_RAG_CHARS]

    try:
        llm = get_llm(provider)
        result = chain_fn(llm).invoke(capped_inputs)
        return {label: result.strip()}
    except Exception as exc:
        logger.error(f"{label} node failed: {exc}")
        return {"errors": state["errors"] + [f"{label} failed: {exc}"]}


def overview_node(state: AgentState) -> dict:
    logger.info("[Node] overview")
    return _invoke(overview_chain, state["provider"], {
        "topic": state["topic"],
        "search_results": state["search_text"],
        "rag_context": state["rag_context"],
    }, state, "overview")


def key_concepts_node(state: AgentState) -> dict:
    logger.info("[Node] key_concepts")
    return _invoke(key_concepts_chain, state["provider"], {
        "topic": state["topic"],
        "search_results": state["search_text"],
        "rag_context": state["rag_context"],
    }, state, "key_concepts")


def facts_node(state: AgentState) -> dict:
    logger.info("[Node] facts")
    return _invoke(important_facts_chain, state["provider"], {
        "topic": state["topic"],
        "search_results": state["search_text"],
        "rag_context": state["rag_context"],
    }, state, "important_facts")


def roadmap_node(state: AgentState) -> dict:
    logger.info("[Node] roadmap")
    return _invoke(roadmap_chain, state["provider"], {
        "topic": state["topic"],
        "search_results": state["search_text"],
        "rag_context": state["rag_context"],
    }, state, "roadmap")


def summary_node(state: AgentState) -> dict:
    logger.info("[Node] summary")
    return _invoke(summary_chain, state["provider"], {
        "topic": state["topic"],
        "overview": state["overview"],
        "key_concepts": state["key_concepts"],
        "important_facts": state["important_facts"],
    }, state, "summary")


def youtube_node(state: AgentState) -> dict:
    logger.info("[Node] youtube")
    try:
        return {"youtube_videos": search_youtube(state["topic"])}
    except Exception as exc:
        logger.error(f"youtube_node: {exc}")
        return {"youtube_videos": [], "errors": state["errors"] + [f"YouTube: {exc}"]}


# ── Graph ──────────────────────────────────────────────────────────────────────

def _build_graph() -> Any:
    g = StateGraph(AgentState)
    for name, fn in [
        ("exa_search_node", exa_search_node),
        ("rag_retrieve_node", rag_retrieve_node),
        ("overview_node", overview_node),
        ("key_concepts_node", key_concepts_node),
        ("facts_node", facts_node),
        ("roadmap_node", roadmap_node),
        ("summary_node", summary_node),
        ("youtube_node", youtube_node),
    ]:
        g.add_node(name, fn)

    g.set_entry_point("exa_search_node")
    g.add_edge("exa_search_node", "rag_retrieve_node")
    g.add_edge("rag_retrieve_node", "overview_node")
    g.add_edge("overview_node", "key_concepts_node")
    g.add_edge("key_concepts_node", "facts_node")
    g.add_edge("facts_node", "roadmap_node")
    g.add_edge("roadmap_node", "summary_node")
    g.add_edge("summary_node", "youtube_node")
    g.add_edge("youtube_node", END)
    return g.compile()


_graph = _build_graph()


# ── Public API ─────────────────────────────────────────────────────────────────

def run_research(topic: str, provider: str = "groq") -> AgentState:
    """Run the full 8-node research pipeline and return the final state."""
    logger.info(f"Research start — topic: {topic!r}, provider: {provider}")
    t0 = time.perf_counter()
    state = _graph.invoke(_empty_state(topic, provider))
    state["elapsed_seconds"] = round(time.perf_counter() - t0, 1)
    logger.info(f"Research done in {state['elapsed_seconds']}s — errors: {len(state['errors'])}")
    return state