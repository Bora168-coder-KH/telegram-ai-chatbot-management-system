"""Admin dashboard: login, pages, HTMX actions, CSRF, roles and masking."""
import re

from fastapi.testclient import TestClient

from app.web.main import app
from tests.web_helpers import csrf_from, login

PAGES = ("/dashboard", "/users", "/conversations", "/conversations?filter=all", "/faq", "/knowledge",
         "/intents", "/commands", "/broadcast", "/reports", "/settings", "/logs")


def test_pages_need_login():
    with TestClient(app) as client:
        response = client.get("/dashboard", follow_redirects=False)
        assert response.status_code == 303 and response.headers["location"].startswith("/login")
        htmx = client.post("/faq", headers={"HX-Request": "true"}, follow_redirects=False)
        assert htmx.headers.get("HX-Redirect", "").startswith("/login")


def test_wrong_password_is_refused():
    with TestClient(app) as client:
        response = login(client, password="wrong")
        assert response.status_code == 401 and "Wrong email or password" in response.text


def test_all_pages_load_after_login():
    with TestClient(app) as client:
        assert login(client).status_code == 303
        for path in PAGES:
            response = client.get(path)
            assert response.status_code == 200, path
        assert "Total Users" in client.get("/dashboard").text
        assert client.get("/health").json() == {"status": "ok"}


def test_add_and_delete_faq_with_htmx():
    with TestClient(app) as client:
        login(client)
        response = client.post("/faq", data={
            "question": "Where are you?", "answer": "Phnom Penh", "category": "General",
            "keywords": "location,address", "language": "en",
        })
        assert response.status_code == 200
        assert "Where are you?" in response.text
        assert "Where are you?" in client.get("/faq").text
        faq_id = re.search(r'id="faq-(\d+)"', response.text).group(1)
        assert client.delete(f"/faq/{faq_id}").status_code == 200
        assert "Where are you?" not in client.get("/faq").text


def test_post_without_csrf_token_is_refused():
    with TestClient(app) as client:
        login(client)
        del client.headers["X-CSRF-Token"]
        response = client.post("/faq", data={"question": "q", "answer": "a"})
        assert response.status_code == 403


def test_logout():
    with TestClient(app) as client:
        login(client)
        token = client.headers["X-CSRF-Token"]
        client.post("/logout", data={"csrf_token": token}, follow_redirects=False)
        assert client.get("/dashboard", follow_redirects=False).status_code == 303


def test_intents_commands_and_knowledge_pages_work():
    with TestClient(app) as client:
        login(client)
        r = client.post("/intents", data={"name": "Opening Day", "phrases": "when do you open\nkm: ពេលណាបើក",
                                          "response": "We open on {date}.", "entities": ["date"]})
        assert r.status_code == 200 and "opening_day" in r.text and "ពេលណាបើក" in r.text
        test = client.post("/intents/test", data={"text": "I want to book an appointment on 2026-11-02"})
        assert "book_appointment" in test.text and "2026-11-02" in test.text
        cmd = client.post("/commands", data={"name": "/hours", "response": "8 to 5"})
        assert cmd.status_code == 200 and "/hours" in cmd.text
        assert client.post("/commands", data={"name": "start", "response": "x"}).status_code == 400
        article = client.post("/knowledge", data={"title": "Exam rules", "content": "Bring your ID card.",
                                                  "keywords": "exam,id card"})
        assert article.status_code == 200 and "Exam rules" in article.text


def test_reports_export():
    with TestClient(app) as client:
        login(client)
        xlsx = client.get("/reports/export.xlsx")
        assert xlsx.status_code == 200 and xlsx.content[:2] == b"PK"  # a zip file
        pdf = client.get("/reports/export.pdf")
        assert pdf.status_code == 200 and pdf.content[:4] == b"%PDF"


def test_settings_maintenance_mode():
    with TestClient(app) as client:
        login(client)
        page = client.get("/settings").text
        token = csrf_from(page)
        r = client.post("/settings/bot", data={"csrf_token": token, "name": "AI Chatbot", "maintenance_mode": "on"},
                        follow_redirects=False)
        assert r.status_code == 303
        assert "checked" in re.search(r'name="maintenance_mode"[^>]*>', client.get("/settings").text).group()
        client.post("/settings/bot", data={"csrf_token": token, "name": "AI Chatbot"})  # turn it off again
