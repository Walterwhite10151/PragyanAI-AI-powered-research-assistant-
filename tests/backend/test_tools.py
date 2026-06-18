"""
tests/backend/test_tools.py
-----------------------------
Unit tests for backend tools and utilities.
No live API calls — external services are mocked.

Run:
    cd ai_research_agent
    pytest tests/ -v
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from backend.tools.pdf_processor import chunk_text, _clean_html
from backend.tools.exa_search import ExaResult, format_results_for_llm


# ── Exa Search ─────────────────────────────────────────────────────────────────

class TestExaFormatting:
    def test_empty_results(self):
        assert format_results_for_llm([]) == "No search results found."

    def test_single_result(self):
        r = ExaResult(title="AI News", url="https://ai.com", snippet="Great article", content="Full text here", score=0.95)
        out = format_results_for_llm([r])
        assert "[Source 1]" in out
        assert "AI News" in out
        assert "https://ai.com" in out
        assert "Full text here" in out

    def test_multiple_results_separated(self):
        results = [
            ExaResult("T1", "https://a.com", "S1", "C1", score=0.9),
            ExaResult("T2", "https://b.com", "S2", "C2", score=0.8),
        ]
        out = format_results_for_llm(results)
        assert "[Source 1]" in out
        assert "[Source 2]" in out
        assert "---" in out

    def test_published_date_included(self):
        r = ExaResult("T", "https://x.com", "S", "C", published_date="2024-06-01", score=0.7)
        out = format_results_for_llm([r])
        assert "2024-06-01" in out

    def test_falls_back_to_snippet_when_no_content(self):
        r = ExaResult("T", "https://x.com", "Snippet only", content="", score=0.5)
        out = format_results_for_llm([r])
        assert "Snippet only" in out


# ── PDF Processor ──────────────────────────────────────────────────────────────

class TestChunking:
    def test_empty_text(self):
        assert chunk_text("") == []

    def test_short_text_single_chunk(self):
        assert chunk_text("Hello world", chunk_size=800) == ["Hello world"]

    def test_long_text_multiple_chunks(self):
        chunks = chunk_text("A" * 3000, chunk_size=800, overlap=150)
        assert len(chunks) > 1

    def test_chunk_max_size_respected(self):
        chunks = chunk_text("B" * 5000, chunk_size=500, overlap=100)
        for c in chunks:
            assert len(c) <= 500

    def test_overlap_is_shared(self):
        text = "X" * 2000
        chunks = chunk_text(text, chunk_size=500, overlap=100)
        assert len(chunks) >= 2
        # The first 100 chars of chunk[1] equal the last 100 chars of chunk[0]
        assert chunks[1][:100] == chunks[0][-100:]

    def test_strips_whitespace(self):
        chunks = chunk_text("   hello world   ", chunk_size=800)
        assert chunks[0] == "hello world"

    def test_clean_html_removes_scripts(self):
        html = "<html><body><script>evil()</script><p>Clean text</p></body></html>"
        assert "evil()" not in _clean_html(html)
        assert "Clean text" in _clean_html(html)

    def test_clean_html_removes_tags(self):
        html = "<div><h1>Title</h1><p>Body</p></div>"
        result = _clean_html(html)
        assert "<" not in result
        assert "Title" in result
        assert "Body" in result


# ── Storage ────────────────────────────────────────────────────────────────────

class TestStorage:
    @pytest.fixture(autouse=True)
    def patch_paths(self, tmp_path, monkeypatch):
        from backend.core import config as cfg
        monkeypatch.setattr(cfg.settings, "conversation_history_path", str(tmp_path))
        import importlib
        import backend.utils.storage as st
        importlib.reload(st)
        self.storage = st

    def test_save_and_load_session(self):
        sid = self.storage.save_session("Quantum Computing", "groq", {"overview": "QC overview"})
        history = self.storage.load_history()
        assert len(history) == 1
        assert history[0]["topic"] == "Quantum Computing"
        assert history[0]["session_id"] == sid
        assert history[0]["provider"] == "groq"

    def test_get_session_by_id(self):
        sid = self.storage.save_session("Rust", "gemini", {})
        session = self.storage.get_session(sid)
        assert session is not None
        assert session["topic"] == "Rust"

    def test_delete_history(self):
        self.storage.save_session("Topic", "groq", {})
        self.storage.delete_history()
        assert self.storage.load_history() == []

    def test_history_capped_at_50(self):
        for i in range(60):
            self.storage.save_session(f"Topic {i}", "groq", {})
        assert len(self.storage.load_history()) == 50

    def test_preferences_defaults(self):
        prefs = self.storage.load_preferences()
        assert "default_provider" in prefs
        assert "auto_youtube" in prefs

    def test_save_and_load_preferences(self):
        self.storage.save_preferences({"default_provider": "gemini", "auto_youtube": False})
        prefs = self.storage.load_preferences()
        assert prefs["default_provider"] == "gemini"
        assert prefs["auto_youtube"] is False

    def test_preferences_merge_keeps_defaults(self):
        self.storage.save_preferences({"theme": "light"})
        prefs = self.storage.load_preferences()
        assert "auto_youtube" in prefs  # default still present

    def test_reset_preferences(self):
        self.storage.save_preferences({"default_provider": "gemini"})
        self.storage.reset_preferences()
        prefs = self.storage.load_preferences()
        assert prefs["default_provider"] == "groq"


# ── Config ─────────────────────────────────────────────────────────────────────

class TestConfig:
    def test_exa_key_field_exists(self):
        from backend.core.config import settings
        assert hasattr(settings, "exa_api_key")

    def test_groq_key_field_exists(self):
        from backend.core.config import settings
        assert hasattr(settings, "groq_api_key")

    def test_gemini_key_field_exists(self):
        from backend.core.config import settings
        assert hasattr(settings, "gemini_api_key")

    def test_cors_origins_parsed(self):
        from backend.core.config import settings
        origins = settings.get_cors_origins()
        assert isinstance(origins, list)
        assert len(origins) >= 1
