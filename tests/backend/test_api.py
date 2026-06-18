"""
tests/backend/test_api.py
--------------------------
FastAPI route integration tests using TestClient.
External services (Exa, Groq, Gemini, YouTube) are mocked.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestStatusEndpoint:
    def test_root(self):
        r = client.get("/")
        assert r.status_code == 200
        assert "AI Research Agent" in r.json()["name"]

    def test_status(self):
        r = client.get("/api/status")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "providers" in data
        assert "vector_store_chunks" in data


class TestResearchEndpoint:
    @patch("backend.api.routes.research.run_research")
    @patch("backend.api.routes.research.save_session", return_value="abc12345")
    def test_research_success(self, mock_save, mock_run):
        mock_run.return_value = {
            "topic": "Python",
            "provider": "groq",
            "exa_results": [],
            "overview": "Python is great.",
            "key_concepts": "- Interpreted",
            "important_facts": "- Created 1991",
            "roadmap": "Phase 1: Basics",
            "summary": "Bottom line: Learn Python.",
            "youtube_videos": [],
            "errors": [],
            "elapsed_seconds": 12.3,
        }
        r = client.post("/api/research", json={"topic": "Python", "provider": "groq"})
        assert r.status_code == 200
        data = r.json()
        assert data["topic"] == "Python"
        assert data["session_id"] == "abc12345"
        assert data["elapsed_seconds"] == 12.3

    def test_research_empty_topic(self):
        r = client.post("/api/research", json={"topic": "", "provider": "groq"})
        assert r.status_code == 422

    def test_research_invalid_provider(self):
        r = client.post("/api/research", json={"topic": "Test", "provider": "openai"})
        assert r.status_code == 422


class TestPDFEndpoints:
    def test_upload_non_pdf_rejected(self):
        r = client.post(
            "/api/pdf/upload",
            files={"file": ("test.txt", b"hello", "text/plain")},
            data={"provider": "groq"},
        )
        assert r.status_code == 400

    def test_vector_store_stats(self):
        r = client.get("/api/pdf/stats")
        assert r.status_code == 200
        assert "total_chunks" in r.json()

    def test_clear_vector_store(self):
        r = client.delete("/api/pdf/clear")
        assert r.status_code == 200
        assert "cleared" in r.json()["message"]

    @patch("backend.api.routes.pdf.answer_pdf_question", return_value="42 is the answer.")
    def test_ask_question(self, mock_answer):
        r = client.post("/api/pdf/question", json={"question": "What is the answer?", "provider": "groq"})
        assert r.status_code == 200
        data = r.json()
        assert data["answer"] == "42 is the answer."


class TestHistoryEndpoints:
    def test_get_empty_history(self):
        with patch("backend.api.routes.history.load_history", return_value=[]):
            r = client.get("/api/history")
            assert r.status_code == 200
            assert r.json() == []

    def test_clear_history(self):
        with patch("backend.api.routes.history.delete_history"):
            r = client.delete("/api/history")
            assert r.status_code == 200

    def test_get_missing_session(self):
        with patch("backend.api.routes.history.get_session", return_value=None):
            r = client.get("/api/history/nonexistent")
            assert r.status_code == 404


class TestPreferencesEndpoints:
    def test_get_preferences(self):
        r = client.get("/api/preferences")
        assert r.status_code == 200
        assert "preferences" in r.json()

    def test_update_preferences(self):
        r = client.put("/api/preferences", json={"default_provider": "gemini"})
        assert r.status_code == 200
        assert r.json()["preferences"]["default_provider"] == "gemini"

    def test_reset_preferences(self):
        r = client.delete("/api/preferences/reset")
        assert r.status_code == 200
        assert "preferences" in r.json()
