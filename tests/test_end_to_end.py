"""End to end: Telegram user -> bot routing -> fallback -> human handoff -> agent reply on the
dashboard -> resolved -> the Resolution Rate on the dashboard counts it."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.bot import handlers
from app.db import SessionLocal
from app.models import Conversation, TelegramUser
from app.services import telegram
from app.services.stats import resolution
from app.web.main import app
from tests.web_helpers import login

UID = 7777001


def say(text: str):
    message = SimpleNamespace(text=text, answer=AsyncMock(),
                              from_user=SimpleNamespace(id=UID, username="e2e", full_name="End To End"))

    async def run():
        async with SessionLocal() as session:
            if text.startswith("/start"):
                await handlers.cmd_start(message, session)
            elif text == "🧑‍💼 Human Support":
                await handlers.on_menu_button(message, session)
            else:
                await handlers.on_text(message, session)
    asyncio.run(run())
    return message.answer.call_args.args[0]


def conversation_id() -> int:
    async def run():
        async with SessionLocal() as session:
            user = (await session.execute(select(TelegramUser).where(TelegramUser.telegram_user_id == UID))).scalar_one()
            return (await session.execute(select(Conversation.id).where(Conversation.user_id == user.id)
                                          .order_by(Conversation.id.desc()))).scalars().first()
    return asyncio.run(run())


def resolved_count() -> int:
    async def run():
        async with SessionLocal() as session:
            return (await resolution(session))["resolved"]
    return asyncio.run(run())


def test_question_to_resolved_support_request(monkeypatch):
    bot = SimpleNamespace(send_message=AsyncMock())
    monkeypatch.setattr(telegram, "get_bot", lambda: bot)

    with TestClient(app) as client:  # starts the app: migrations + seed data
        login(client)
        say("/start")
        assert "Monday" in say("What are your opening hours?")  # FAQ
        assert "do not have an answer" in say("my certificate has a wrong birth date zqx")  # fallback
        say("🧑‍💼 Human Support")
        cid = conversation_id()
        before = resolved_count()

        queue = client.get("/conversations").text
        assert f"/conversations/{cid}" in queue  # it is in the agent queue

        # the agent answers from the dashboard; the bot stays quiet while an agent handles it
        client.post(f"/conversations/{cid}/reply", data={"text": "Please send a photo of your ID card."})
        assert "passed to the support agent" in say("ok here it is")
        assert bot.send_message.await_args_list[0].args == (UID, "Please send a photo of your ID card.")

        client.post(f"/conversations/{cid}/status", data={"status": "Resolved"})
        assert resolved_count() == before + 1
        assert "resolved" in bot.send_message.await_args.args[1]  # Status Update notification
        assert "Resolution Rate" in client.get("/dashboard").text
