"""Log a TestClient in to the dashboard (and send the CSRF token on every request)."""
import re

from fastapi.testclient import TestClient

ADMIN = ("admin@example.com", "test-password")  # ADMIN_PASSWORD is set in conftest.py


def csrf_from(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html) or re.search(r'"X-CSRF-Token": "([^"]+)"', html)
    assert match, "no CSRF token in page"
    return match.group(1)


def login(client: TestClient, email: str = ADMIN[0], password: str = ADMIN[1]):
    token = csrf_from(client.get("/login").text)
    response = client.post("/login", data={"email": email, "password": password, "csrf_token": token},
                           follow_redirects=False)
    page = client.get("/dashboard")
    if page.status_code == 200 and "X-CSRF-Token" in page.text:
        client.headers["X-CSRF-Token"] = csrf_from(page.text)
    return response
