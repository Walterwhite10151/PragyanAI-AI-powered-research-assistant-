"""
backend/api/schemas.py
-----------------------
All Pydantic request and response models for the FastAPI routes.
"""

from __future__ import annotations

from typing import List, Optional, Any
from pydantic import BaseModel, Field


# ── Research ───────────────────────────────────────────────────────────────────

class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=300)
    provider: str = Field(default="groq", pattern="^(groq|gemini)$")


class SourceItem(BaseModel):
    title: str
    url: str
    snippet: str
    published_date: Optional[str] = None
    score: float = 0.0


class VideoItem(BaseModel):
    title: str
    channel: str
    url: str
    thumbnail: str
    duration: str
    views: str


class ResearchResponse(BaseModel):
    topic: str
    provider: str
    overview: str
    key_concepts: str
    important_facts: str
    roadmap: str
    summary: str
    sources: List[SourceItem]
    youtube_videos: List[VideoItem]
    errors: List[str]
    elapsed_seconds: float
    session_id: str


# ── PDF ────────────────────────────────────────────────────────────────────────

class PDFUploadResponse(BaseModel):
    filename: str
    pages: int
    chunks: int
    summary: str
    error: Optional[str] = None


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    provider: str = Field(default="groq", pattern="^(groq|gemini)$")


class QuestionResponse(BaseModel):
    question: str
    answer: str


# ── History ────────────────────────────────────────────────────────────────────

class SessionMeta(BaseModel):
    session_id: str
    topic: str
    provider: str
    timestamp: str


class SessionDetail(SessionMeta):
    result: dict


# ── Preferences ────────────────────────────────────────────────────────────────

class PreferencesRequest(BaseModel):
    default_provider: Optional[str] = None
    research_depth: Optional[str] = None
    auto_youtube: Optional[bool] = None
    show_sources: Optional[bool] = None
    theme: Optional[str] = None


class PreferencesResponse(BaseModel):
    preferences: dict


# ── Status ─────────────────────────────────────────────────────────────────────

class ProviderInfo(BaseModel):
    id: str
    name: str
    model: str
    configured: bool
    description: str


class StatusResponse(BaseModel):
    status: str
    providers: List[ProviderInfo]
    vector_store_chunks: int
    exa_configured: bool


# ── Vector Store ───────────────────────────────────────────────────────────────

class VectorStoreStats(BaseModel):
    total_chunks: int


class ClearResponse(BaseModel):
    message: str
