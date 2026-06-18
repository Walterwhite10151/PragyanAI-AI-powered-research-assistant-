"""
backend/tools/exa_search.py
----------------------------
Exa-powered web search tool.

Exa (https://exa.ai) is a neural search engine that returns semantically
relevant results with full-page content — far better than keyword search
for research tasks.

Features used:
  • Neural search  – semantic understanding of the query.
  • Text contents  – full extracted page text (no scraping needed).
  • Highlights     – Exa's AI-extracted key sentences per result.
  • Auto date filtering – recency bias for current topics.

--------------------------------------------------------------------------
CHANGES vs. the original version (fixes 500 / 404 / 412 / 429 behaviour):

  1. Errors are now classified by HTTP status into typed exceptions
     (ExaRateLimitError, ExaAuthError, ExaInvalidRequestError,
     ExaNotFoundError, ExaServiceError) instead of leaking a bare
     `Exception` up to the caller. Your API route can catch these
     specifically and return the right status code to the client
     instead of a generic 500.
  2. Retries now only happen for genuinely transient failures — 429
     (rate limit) and 5xx (server error) — with a longer, jittered
     backoff appropriate for Exa's ~10 QPS default limit. 4xx client
     errors (400/404/412/422) fail immediately, since retrying a
     malformed request three times just delays the inevitable.
  3. `use_autoprompt` is deprecated by Exa and no longer sent to the
     API (kept as a no-op kwarg so existing call sites don't break).
     Default search `type` switched from "neural" to "auto", which
     Exa now auto-routes to the best underlying method.
  4. Every failure is logged with the original exception text so 404s
     and 412s caused by SDK/API version drift are easy to diagnose
     instead of disappearing into a retry loop.
--------------------------------------------------------------------------
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timedelta

from exa_py import Exa
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from backend.core.config import settings
from backend.utils.logger import logger


# --------------------------------------------------------------------------
# Typed errors
# --------------------------------------------------------------------------

class ExaSearchError(Exception):
    """Base class for all errors raised by this module."""

    def __init__(self, message: str, status_code: Optional[int] = None, original: Optional[Exception] = None):
        super().__init__(message)
        self.status_code = status_code
        self.original = original


class ExaAuthError(ExaSearchError):
    """401 / 403 — bad or missing EXA_API_KEY."""


class ExaNotFoundError(ExaSearchError):
    """404 — wrong endpoint, usually an SDK/API version mismatch."""


class ExaInvalidRequestError(ExaSearchError):
    """400 / 412 / 422 — the request body Exa received was malformed."""


class ExaRateLimitError(ExaSearchError):
    """429 — too many requests. Safe to retry with backoff."""


class ExaServiceError(ExaSearchError):
    """5xx, or a network-level failure with no status code at all. Safe to retry."""


def _status_code_from_exception(exc: Exception) -> Optional[int]:
    """Best-effort extraction of an HTTP status code from an arbitrary
    exception. Handles both typed HTTP-client exceptions (requests/httpx,
    which expose `.response.status_code`) and the bare `Exception` style
    that older exa_py versions raise with the code embedded in the message."""
    response = getattr(exc, "response", None)
    if response is not None and hasattr(response, "status_code"):
        try:
            return int(response.status_code)
        except (TypeError, ValueError):
            pass

    match = re.search(r"\b(4\d{2}|5\d{2})\b", str(exc))
    if match:
        return int(match.group(1))
    return None


def _raise_classified(exc: Exception) -> None:
    """Re-raise a raw exception from exa_py / the network stack as one of
    our typed errors, so both the retry logic and the caller can react to
    *why* the call failed instead of just that it failed."""
    status = _status_code_from_exception(exc)
    logger.error(f"Exa request failed (status={status}): {exc}")

    if status == 429:
        raise ExaRateLimitError(
            "Exa rate limit exceeded (429).", status_code=429, original=exc
        ) from exc
    if status in (401, 403):
        raise ExaAuthError(
            f"Exa rejected the request as unauthorized ({status}). Check EXA_API_KEY.",
            status_code=status, original=exc,
        ) from exc
    if status == 404:
        raise ExaNotFoundError(
            "Exa returned 404. This usually means the installed exa_py "
            "version doesn't match the request shape being sent — run "
            "`pip show exa_py` and compare against docs.exa.ai.",
            status_code=404, original=exc,
        ) from exc
    if status in (400, 412, 422):
        raise ExaInvalidRequestError(
            f"Exa rejected the request as malformed ({status}): {exc}",
            status_code=status, original=exc,
        ) from exc
    if status is not None and status >= 500:
        raise ExaServiceError(
            f"Exa's API had a server-side error ({status}).", status_code=status, original=exc
        ) from exc

    # No status code at all -> network-level failure (timeout, DNS, reset).
    raise ExaServiceError(f"Could not reach Exa's API: {exc}", status_code=None, original=exc) from exc


def _is_retryable(exc: BaseException) -> bool:
    """Only rate limits and server/network errors are worth retrying.
    A 400/404/412/422 will fail again immediately, so don't waste time on it."""
    return isinstance(exc, (ExaRateLimitError, ExaServiceError))


@dataclass
class ExaResult:
    title: str
    url: str
    snippet: str                        # highlights or first 400 chars of text
    content: str = field(default="", repr=False)
    published_date: Optional[str] = None
    author: Optional[str] = None
    score: float = 0.0


_client: Exa | None = None


def _get_client() -> Exa:
    global _client
    if _client is None:
        if not settings.exa_api_key:
            raise ValueError(
                "EXA_API_KEY is not set. Get a free key at https://exa.ai"
            )
        _client = Exa(api_key=settings.exa_api_key)
    return _client


@retry(
    retry=retry_if_exception(_is_retryable),
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=2, max=20),
    reraise=True,
)
def search_exa(
    query: str,
    max_results: int | None = None,
    use_autoprompt: bool = False,  # deprecated by Exa, kept as a no-op for compatibility
    include_domains: list[str] | None = None,
    days_back: int | None = None,
    search_type: str = "auto",  # Exa now recommends "auto" over forcing "neural"
) -> List[ExaResult]:
    """
    Search the web with Exa and return enriched results.

    Args:
        query:           Research query string.
        max_results:     Number of results (default: EXA_MAX_RESULTS from settings).
        use_autoprompt:  Deprecated by Exa; accepted but ignored, no longer sent.
        include_domains: Restrict to specific domains (e.g. ["arxiv.org"]).
        days_back:       Only return results from the past N days.
        search_type:     "auto" (default), "neural", "keyword", or "fast".

    Returns:
        List of ExaResult with full page content and highlights.

    Raises:
        ExaAuthError, ExaNotFoundError, ExaInvalidRequestError,
        ExaRateLimitError, ExaServiceError — see class docstrings above.
    """
    if not query or not query.strip():
        raise ExaInvalidRequestError("Query must be a non-empty string.", status_code=400)

    client = _get_client()
    n = max_results or settings.exa_max_results
    logger.info(f"Exa search: {query!r} (max={n}, type={search_type})")

    kwargs: dict = {
        "num_results": n,
        "type": search_type,
    }

    if include_domains:
        kwargs["include_domains"] = include_domains

    if days_back:
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        kwargs["start_published_date"] = start_date

    try:
        response = client.search_and_contents(
            query,
            text={"max_characters": 800},
            highlights={"num_sentences": 3, "highlights_per_url": 2}
            if settings.exa_use_highlights
            else False,
            **kwargs,
        )
    except ExaSearchError:
        raise
    except Exception as exc:
        _raise_classified(exc)
        return []  # unreachable — _raise_classified always raises

    results: List[ExaResult] = []
    for item in response.results:
        highlights = getattr(item, "highlights", None) or []
        if highlights:
            snippet = " … ".join(highlights[:2])
        else:
            text = getattr(item, "text", "") or ""
            snippet = text[:400]

        results.append(
            ExaResult(
                title=item.title or "",
                url=item.url or "",
                snippet=snippet,
                content=getattr(item, "text", "") or snippet,
                published_date=getattr(item, "published_date", None),
                author=getattr(item, "author", None),
                score=getattr(item, "score", 0.0) or 0.0,
            )
        )

    logger.info(f"Exa returned {len(results)} results for: {query!r}")
    return results


def format_results_for_llm(results: List[ExaResult]) -> str:
    """Serialise Exa results into a single text block for LLM prompts."""
    if not results:
        return "No search results found."

    parts: List[str] = []
    for i, r in enumerate(results, 1):
        date_str = f" (published: {r.published_date})" if r.published_date else ""
        author_str = f" | Author: {r.author}" if r.author else ""
        body = r.content if r.content else r.snippet
        parts.append(
            f"[Source {i}]{date_str}{author_str}\n"
            f"Title: {r.title}\n"
            f"URL: {r.url}\n"
            f"Content:\n{body}"
        )

    return "\n\n---\n\n".join(parts)