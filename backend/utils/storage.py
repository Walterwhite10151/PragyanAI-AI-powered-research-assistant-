"""
backend/utils/storage.py
------------------------
JSON-based local persistence for conversation history and user preferences.
No database required — files live under data/conversation_history/.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from backend.core.config import settings
from backend.utils.logger import logger

_HISTORY_FILE = Path(settings.conversation_history_path) / "history.json"
_PREFS_FILE = Path(settings.conversation_history_path) / "preferences.json"

_DEFAULT_PREFS: dict = {
    "default_provider": "groq",
    "research_depth": "standard",
    "auto_youtube": True,
    "show_sources": True,
    "theme": "dark",
}


def _load(path: Path) -> Any:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning(f"Corrupt JSON at {path}; resetting.")
    return None


def _save(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ── History ────────────────────────────────────────────────────────────────────

def load_history() -> list[dict]:
    data = _load(_HISTORY_FILE)
    return data if isinstance(data, list) else []


def save_session(topic: str, provider: str, result: dict) -> str:
    history = load_history()
    session_id = str(uuid.uuid4())[:8]
    history.append({
        "session_id": session_id,
        "topic": topic,
        "provider": provider,
        "timestamp": datetime.now().isoformat(),
        "result": result,
    })
    _save(_HISTORY_FILE, history[-50:])
    logger.info(f"Session {session_id} saved — topic: {topic!r}")
    return session_id


def get_session(session_id: str) -> dict | None:
    for entry in load_history():
        if entry.get("session_id") == session_id:
            return entry
    return None


def delete_history() -> None:
    _save(_HISTORY_FILE, [])


# ── Preferences ────────────────────────────────────────────────────────────────

def load_preferences() -> dict:
    data = _load(_PREFS_FILE)
    return {**_DEFAULT_PREFS, **(data if isinstance(data, dict) else {})}


def save_preferences(prefs: dict) -> dict:
    merged = {**load_preferences(), **prefs}
    _save(_PREFS_FILE, merged)
    return merged


def reset_preferences() -> dict:
    _save(_PREFS_FILE, _DEFAULT_PREFS)
    return dict(_DEFAULT_PREFS)
