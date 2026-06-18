"""
backend/core/config.py
-----------------------
Centralised, type-safe configuration via pydantic-settings.
All values are read from environment variables or a .env file.

CHANGE: env_file is now an absolute path anchored to this file's own
location (backend/), instead of a bare ".env" string. A bare relative
path is resolved against the current working directory at process
start — which silently broke EXA_API_KEY/GROQ_API_KEY loading the
moment uvicorn started being launched from the project root instead
of from inside backend/. Anchoring it here means it works identically
regardless of which directory you run uvicorn from.
"""

from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

_BACKEND_DIR = Path(__file__).resolve().parent.parent  # backend/core/config.py -> backend/


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── LLM ───────────────────────────────────────────────────
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")

    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.0-flash-exp", alias="GEMINI_MODEL")

    default_llm_provider: str = Field(default="groq", alias="DEFAULT_LLM_PROVIDER")

    # ── Exa Search ────────────────────────────────────────────
    exa_api_key: str = Field(default="", alias="EXA_API_KEY")
    exa_max_results: int = Field(default=5, alias="EXA_MAX_RESULTS")
    exa_use_highlights: bool = Field(default=True, alias="EXA_USE_HIGHLIGHTS")

    # ── Embeddings ────────────────────────────────────────────
    embedding_model: str = Field(default="all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")

    # ── ChromaDB ──────────────────────────────────────────────
    chroma_db_path: str = Field(default="./data/chroma_db", alias="CHROMA_DB_PATH")
    chroma_collection_name: str = Field(default="research_docs", alias="CHROMA_COLLECTION_NAME")

    # ── Storage ───────────────────────────────────────────────
    conversation_history_path: str = Field(default="./data/conversation_history", alias="CONVERSATION_HISTORY_PATH")
    uploads_path: str = Field(default="./data/uploads", alias="UPLOADS_PATH")
    logs_path: str = Field(default="./logs", alias="LOGS_PATH")

    # ── YouTube ───────────────────────────────────────────────
    max_youtube_results: int = Field(default=5, alias="MAX_YOUTUBE_RESULTS")

    # ── Agent ─────────────────────────────────────────────────
    summary_max_tokens: int = Field(default=2048, alias="SUMMARY_MAX_TOKENS")
    research_temperature: float = Field(default=0.3, alias="RESEARCH_TEMPERATURE")

    # ── FastAPI ───────────────────────────────────────────────
    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        alias="CORS_ORIGINS",
    )

    def get_cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    def ensure_dirs(self) -> None:
        for attr in ("chroma_db_path", "conversation_history_path", "uploads_path", "logs_path"):
            Path(getattr(self, attr)).mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()