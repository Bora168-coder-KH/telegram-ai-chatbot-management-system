"""docs/demo-script.md, steps 1-11, played in the script's order through the bot handlers and the dashboard.

The order matters: after the form (step 6) an agent owns the conversation, so the bot only answers
again after the request is resolved (step 9). Telegram is a mock.
"""
import asyncio
import re
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
from sqlalchemy import select, update

from app.bot import handlers
from app.db import SessionLocal
from app.mock_data import MOCK_FAQS_EN, MOCK_FAQS_KM
from app.models import FAQ, Agent, Conversation, TelegramUser, UnknownQuestion
from app.services import broadcast, telegram
from app.web.main import app
from tests.web_helpers import login

UID = 7300001
STUDENT = SimpleNamespace(id=UID, username="demo_student", full_name="Demo Student")


def _run(fn):
    async def run():
        async with SessionLocal() as session:
            return await fn(session)
    return asyncio.run(run())


def text(message: str, menu: bool = False) -> SimpleNamespace:
    """The student types (or taps a menu button); returns the fake message with the bot's answers."""
    msg = SimpleNamespace(text=message, from_user=STUDENT, answer=AsyncMock())

    async def run(session):
        if message.startswith("/start"):
            await handlers.cmd_start(msg, session)
        elif menu:
            await handlers.on_menu_button(msg, session)
        else:
            await handlers.on_text(msg, session)
    _run(run)
    return msg


def tap(data: str) -> SimpleNamespace:
    """The student taps an inline button."""
    message = SimpleNamespace(answer=AsyncMock(), edit_text=AsyncMock(), edit_reply_markup=AsyncMock())
    callback = SimpleNamespace(data=data, from_user=STUDENT, message=message, answer=AsyncMock())
    handler = {"lang": handlers.on_language, "faqcat": handlers.on_faq_category, "faq": handlers.on_faq,
               "fb": handlers.on_feedback, "form": handlers.on_form_confirm}[data.split(":")[0]]
    _run(lambda session: handler(callback, session))
    return message


def last(msg) -> str:
    return msg.answer.call_args.args[0]


def buttons(markup) -> list[str]:
    return [b.callback_data for row in markup.inline_keyboard for b in row]


def _faq(faqs: dict, category: str, starts: str, language: str) -> FAQ:
    question, answer, keywords = next(item for item in faqs[category] if item[0].startswith(starts))
    return FAQ(question=question, answer=answer, category=category, keywords=keywords, language=language)


async def _setup(session):
    # the two payment FAQs the demo uses (the full mock set is loaded with python -m app.mock_data)
    for faq in (_faq(MOCK_FAQS_KM, "Payment", "តើខ្ញុំអាចបង់ជាដំណាក់កាល", "km"),
                _faq(MOCK_FAQS_EN, "Payment", "Can I pay in installments", "en")):
        if not (await session.execute(select(FAQ).where(FAQ.question == faq.question))).scalar_one_or_none():
            session.add(faq)
    await session.execute(update(Agent).values(availability="available"))
    await session.commit()


def test_demo_script_in_order(monkeypatch):
    bot = SimpleNamespace(send_message=AsyncMock())
    monkeypatch.setattr(telegram, "get_bot", lambda: bot)
    monkeypatch.setattr(broadcast, "SEND_DELAY", 0)
    monkeypatch.setattr(handlers, "Message", SimpleNamespace)  # fake messages pass the isinstance checks

    with TestClient(app) as client:  # migrations + seed data
        _run(_setup)

        # 1. /start, choose Khmer
        assert "language" in last(text("/start")).lower()
        assert "សូមស្វាគមន៍" in last(tap("lang:km"))

        # 2. FAQ -> Payment -> a question -> thumbs up
        categories = text("📚 FAQ", menu=True).answer.call_args.kwargs["reply_markup"]
        assert "faqcat:Payment" in buttons(categories)
        questions = tap("faqcat:Payment").edit_text.call_args.kwargs["reply_markup"]
        faq_button = next(b for b in buttons(questions) if b.startswith("faq:"))
        answer = tap(faq_button)
        assert "fb:5:" in buttons(answer.answer.call_args.kwargs["reply_markup"])[0]
        tap("fb:5:0")

        # 3. switch to English, typed paraphrase
        tap("lang:en")
        assert "installment" in last(text("can i pay monthly instead of all at once")).lower()

        # 4. intent with a date
        assert "2026-11-02" in last(text("I want to book an appointment on 2026-11-02"))

        # 5. unknown question -> fallback, saved as unanswered
        unknown = text("is there a bus to campus")
        assert "do not have an answer" in last(unknown)
        assert "menu:human" in buttons(unknown.answer.call_args.kwargs["reply_markup"])

        # 6. the form with two invalid answers
        assert "Step 1/4" in last(text("📝 Send a Request", menu=True))
        assert "real name" in last(text("R2"))
        text("Sok Dara")
        assert "not valid" in last(text("123"))
        text("012 345 678")
        text("dara@example.com")
        assert "Sok Dara" in last(text("I need my certificate"))
        assert "Thank you" in last(tap("form:yes"))

        # 7. dashboard shows the unanswered question
        login(client)
        assert "is there a bus to campus" in client.get("/dashboard").text

        # 8. the request is in the queue, auto-assigned; the agent replies
        cid = _run(lambda s: _conversation_id(s))
        queue = client.get("/conversations").text
        assert f"/conversations/{cid}" in queue and "Assigned" in queue
        client.post(f"/conversations/{cid}/reply", data={"text": "Hello Dara, which certificate do you need?"})
        assert bot.send_message.await_args.args == (UID, "Hello Dara, which certificate do you need?")
        assert "passed to the support agent" in last(text("My course certificate please"))

        # 9. resolve -> the student is told
        client.post(f"/conversations/{cid}/status", data={"status": "Resolved"})
        assert "resolved" in bot.send_message.await_args.args[1]

        # 10. add a FAQ for the unanswered question; the bot now answers it
        prefilled = client.get("/faq?question=is%20there%20a%20bus%20to%20campus").text
        assert 'value="is there a bus to campus"' in prefilled
        client.post("/faq", data={"question": "Is there a bus to campus?", "answer": "Yes, bus line 7 stops at the gate.",
                                  "keywords": "bus to campus", "language": "en", "category": "General"})
        assert "bus line 7" in last(text("is there a bus to campus"))

        # 11. broadcast to all users reaches the student
        user_id = _run(lambda s: _user_id(s))
        preview = client.post("/broadcast/preview", data={"message": "Classes start on Monday", "audience": "all"})
        assert "Classes start on Monday" in preview.text
        client.post("/broadcast", data={"message": "Classes start on Monday", "audience": "selected",
                                        "user_ids": str(user_id)})
        for _ in range(100):  # "send now" runs as a background task in the app's event loop
            if bot.send_message.await_args.args == (UID, "Classes start on Monday"):
                break
            time.sleep(0.05)
        assert bot.send_message.await_args.args == (UID, "Classes start on Monday")

    async def unanswered(session):
        row = (await session.execute(
            select(UnknownQuestion).where(UnknownQuestion.question == "is there a bus to campus"))).scalar_one()
        return row.frequency
    assert _run(unanswered) == 1  # asked twice, but the second time it was answered by the new FAQ


async def _user_id(session) -> int:
    return (await session.execute(select(TelegramUser.id).where(TelegramUser.telegram_user_id == UID))).scalar_one()


async def _conversation_id(session) -> int:
    return (await session.execute(
        select(Conversation.id).where(Conversation.user_id == await _user_id(session))
        .order_by(Conversation.id.desc()))).scalars().first()


def test_suspended_by_spam_can_be_reactivated():
    """The rehearsal problem from the script: re-activate the user from the Users page."""
    async def suspend(session):
        user = (await session.execute(select(TelegramUser).where(TelegramUser.telegram_user_id == UID))).scalar_one()
        user.status = "Suspended"
        await session.commit()
        return user.id
    with TestClient(app) as client:
        text("/start")
        user_id = _run(suspend)
        login(client)
        row = client.post(f"/users/{user_id}/status", data={"status": "Active"}).text
        assert re.search(r'<option value="Active" selected', row)
