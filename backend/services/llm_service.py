
"""
backend/services/llm_service.py
--------------------------------
Unified LLM interface supporting Groq and Gemini.
Both providers are wired through LangChain so the agent chains
are completely provider-agnostic — swap at runtime via the API.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.core.config import settings
from backend.utils.logger import logger

LLMProvider = Literal["groq", "gemini"]


@lru_cache(maxsize=4)
def get_llm(provider: LLMProvider | None = None, temperature: float = 0.3) -> BaseChatModel:
    """
    Return a cached LangChain chat model for the given provider.

    Args:
        provider:    "groq" | "gemini" | None (uses DEFAULT_LLM_PROVIDER).
        temperature: Sampling temperature.

    Returns:
        LangChain BaseChatModel compatible with LCEL chains.
    """
    resolved = provider or settings.default_llm_provider
    logger.info(f"Loading LLM provider: {resolved}")

    if resolved == "groq":
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY is not set. Get one at https://console.groq.com")
        return ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=temperature,
            max_tokens=settings.summary_max_tokens,
        )

    if resolved == "gemini":
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not set. Get one at https://aistudio.google.com")
        return ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key,
            temperature=temperature,
            max_output_tokens=settings.summary_max_tokens,
        )

    raise ValueError(f"Unknown LLM provider: {resolved!r}. Choose 'groq' or 'gemini'.")


def list_available_providers() -> list[dict]:
    """Return providers and whether they are configured."""
    return [
        {
            "id": "groq",
            "name": "Groq",
            "model": settings.groq_model,
            "configured": bool(settings.groq_api_key),
            "description": "Ultra-fast inference via Groq LPU. Free tier available.",
        },
        {
            "id": "gemini",
            "name": "Google Gemini",
            "model": settings.gemini_model,
            "configured": bool(settings.gemini_api_key),
            "description": "Google's multimodal frontier model. Generous free tier.",
        },
    ]

