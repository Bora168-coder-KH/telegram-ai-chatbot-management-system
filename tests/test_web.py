"""Smoke tests for the admin dashboard."""
from fastapi.testclient import TestClient

from app.web.main import app


def test_pages_load():
    with TestClient(app) as client:
        for path in ("/dashboard", "/users", "/faq"):
            response = client.get(path)
            assert response.status_code == 200, path
        assert "Total Users" in client.get("/dashboard").text


def test_add_and_delete_faq_with_htmx():
    with TestClient(app) as client:
        response = client.post("/faq", data={
            "question": "Where are you?", "answer": "Phnom Penh", "category": "General",
            "keywords": "location,address", "language": "en",
        })
        assert response.status_code == 200
        assert "Where are you?" in response.text
        assert "Where are you?" in client.get("/faq").text
