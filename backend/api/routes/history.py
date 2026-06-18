"""
backend/api/routes/history.py
-------------------------------
GET    /api/history           — List all sessions.
GET    /api/history/{id}      — Get one session.
DELETE /api/history           — Delete all history.
GET    /api/preferences       — Load user preferences.
PUT    /api/preferences       — Update user preferences.
DELETE /api/preferences/reset — Reset to defaults.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.api.schemas import (
    SessionMeta, SessionDetail,
    PreferencesRequest, PreferencesResponse, ClearResponse,
)
from backend.utils.storage import (
    load_history, get_session, delete_history,
    load_preferences, save_preferences, reset_preferences,
)

router = APIRouter(prefix="/api", tags=["history"])


# ── History ────────────────────────────────────────────────────────────────────

@router.get("/history", response_model=list[SessionMeta])
async def list_history():
    return [
        SessionMeta(
            session_id=s["session_id"],
            topic=s["topic"],
            provider=s.get("provider", "groq"),
            timestamp=s["timestamp"],
        )
        for s in reversed(load_history())
    ]


@router.get("/history/{session_id}", response_model=SessionDetail)
async def get_history_item(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return SessionDetail(
        session_id=session["session_id"],
        topic=session["topic"],
        provider=session.get("provider", "groq"),
        timestamp=session["timestamp"],
        result=session["result"],
    )


@router.delete("/history", response_model=ClearResponse)
async def clear_history():
    delete_history()
    return ClearResponse(message="History cleared.")


# ── Preferences ────────────────────────────────────────────────────────────────

@router.get("/preferences", response_model=PreferencesResponse)
async def get_preferences():
    return PreferencesResponse(preferences=load_preferences())


@router.put("/preferences", response_model=PreferencesResponse)
async def update_preferences(req: PreferencesRequest):
    updates = req.model_dump(exclude_none=True)
    merged = save_preferences(updates)
    return PreferencesResponse(preferences=merged)


@router.delete("/preferences/reset", response_model=PreferencesResponse)
async def reset_prefs():
    return PreferencesResponse(preferences=reset_preferences())
