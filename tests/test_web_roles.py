"""Roles and permissions, data masking, auto logout, agent reply and broadcast from the dashboard."""
import asyncio
import re
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.config import settings
from app.db import SessionLocal
from app.models import Conversation, Message, Role, Source, TelegramUser
from app.services import broadcast, telegram
from app.services.users import get_or_create_user, get_open_conversation
from app.web.main import app
from app.web.routes import auth
from tests.web_helpers import csrf_from, login


def _db(coro_fn):
    async def run():
        async with SessionLocal() as session:
            return await coro_fn(session)
    return asyncio.run(run())


def _make_account(client: TestClient, email: str, role: str, agent: bool = False):
    async def role_id(session):
        return (await session.execute(select(Role.id).where(Role.name == role))).scalar_one()
    data = {"csrf_token": csrf_from(client.get("/settings").text), "name": role, "email": email,
            "password": "password123", "role_id": _db(role_id)}
    if agent:
        data["is_agent"] = "on"
    client.post("/settings/admins", data=data)


def _user_with_contact(session):
    async def run():
        user, _ = await get_or_create_user(session, 5550001, "dara_s", "Sok Dara")
        user.phone, user.email = "012345678", "dara@example.com"
        await session.commit()
        return user.id
    return run()


def test_viewer_sees_masked_data_and_cannot_change_things():
    async def log_with_contact(session):
        from app.services import logs
        await logs.activity(session, "Logged form", details="call me on 012 345 678")
    with TestClient(app) as admin_client:
        _db(log_with_contact)
        login(admin_client)
        _make_account(admin_client, "viewer@example.com", "Viewer")
    _db(_user_with_contact)
    with TestClient(app) as client:
        login(client, "viewer@example.com", "password123")
        page = client.get("/users").text
        assert "Sok Dara" not in page and "S** D***" in page
        assert "012345678" not in page and "012***678" in page
        assert "dara@example.com" not in page
        assert "Settings" not in page  # no "edit" permission: no Settings link
        assert client.get("/settings").status_code == 403
        assert client.get("/broadcast").status_code == 403
        assert client.post("/faq", data={"question": "q", "answer": "a"}).status_code == 403
        assert client.get("/reports").status_code == 200  # Viewer has "report"
        assert "012***678" in client.get("/logs?q=Logged").text  # free text in logs is masked too


def test_admin_sees_full_data():
    _db(_user_with_contact)
    with TestClient(app) as client:
        login(client)
        page = client.get("/users").text
        assert "Sok Dara" in page and "012345678" in page


def test_auto_logout_after_inactivity(monkeypatch):
    with TestClient(app) as client:
        login(client)
        assert client.get("/dashboard").status_code == 200
        # every session now counts as idle for too long
        monkeypatch.setattr(settings, "session_timeout_minutes", -1)
        response = client.get("/dashboard", follow_redirects=False)
        assert response.status_code == 303
        assert "inactivity" in client.get("/login").text


def test_login_is_locked_after_repeated_failures():
    auth._failures.clear()
    with TestClient(app) as client:
        for _ in range(auth.MAX_FAILURES):
            login(client, "locked@example.com", "nope")
        assert login(client, "locked@example.com", "nope").status_code == 429
    auth._failures.clear()


def test_agent_replies_from_the_dashboard(monkeypatch):
    bot = SimpleNamespace(send_message=AsyncMock())
    monkeypatch.setattr(telegram, "get_bot", lambda: bot)

    async def conversation_id(session):
        user, _ = await get_or_create_user(session, 5550002, "needs_help", "Needs Help")
        return (await get_open_conversation(session, user)).id
    cid = _db(conversation_id)

    with TestClient(app) as client:
        login(client)
        assert "Open a support request" in client.get(f"/conversations/{cid}").text
        client.post(f"/conversations/{cid}/request")
        panel = client.post(f"/conversations/{cid}/reply", data={"text": "Hello from support"})
        assert panel.status_code == 200 and "In Progress" in panel.text
        assert "Hello from support" in client.get(f"/conversations/{cid}/messages?after=0").text
        resolved = client.post(f"/conversations/{cid}/status", data={"status": "Resolved"})
        assert "Resolved" in resolved.text
        bad = client.post(f"/conversations/{cid}/status", data={"status": "Assigned"})
        assert "Cannot change status" in bad.text

    async def check(session):
        conversation = await session.get(Conversation, cid)
        reply = (await session.execute(select(Message).where(
            Message.conversation_id == cid, Message.response_source == Source.AGENT))).scalars().first()
        return conversation.resolution_status, reply.content
    assert _db(check) == ("resolved", "Hello from support")
    assert bot.send_message.await_args_list[0].args == (5550002, "Hello from support")


def test_broadcast_from_the_dashboard(monkeypatch):
    bot = SimpleNamespace(send_message=AsyncMock())
    monkeypatch.setattr(telegram, "get_bot", lambda: bot)
    monkeypatch.setattr(broadcast, "SEND_DELAY", 0)

    async def user_id(session):
        user, _ = await get_or_create_user(session, 5550003, "news", "News Reader")
        return user.id
    uid = _db(user_id)

    with TestClient(app) as client:
        login(client)
        preview = client.post("/broadcast/preview", data={"message": "Exam on Monday", "audience": "selected",
                                                          "user_ids": str(uid)})
        assert "Exam on Monday" in preview.text and "<strong>1</strong> recipient" in preview.text
        history = client.post("/broadcast", data={"message": "Exam on Monday", "audience": "selected",
                                                  "user_ids": str(uid)})
        assert history.status_code == 200 and "Exam on Monday" in history.text
        scheduled = client.post("/broadcast", data={"message": "Later", "audience": "all",
                                                    "scheduled_at": "2099-01-01T08:00"})
        assert "scheduled" in scheduled.text
        past = client.post("/broadcast", data={"message": "Past", "audience": "all",
                                               "scheduled_at": "2000-01-01T08:00"})
        assert past.status_code == 400
        broadcast_id = re.findall(r'hx-post="/broadcast/(\d+)/cancel"', scheduled.text)[0]
        assert "cancelled" in client.post(f"/broadcast/{broadcast_id}/cancel").text

        for _ in range(100):  # the "send now" broadcast runs as a background task in the app's event loop
            if bot.send_message.await_count:
                break
            time.sleep(0.05)
        assert bot.send_message.await_args.args == (5550003, "Exam on Monday")
