"""Intent detection, entity extraction and the Name -> Phone -> Email -> Request form."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from sqlalchemy import select

from app.bot import handlers
from app.db import SessionLocal, init_db
from app.models import Conversation, Source, SupportStatus, TelegramUser
from app.seed import seed_defaults
from app.services.router import route_message
from app.services.users import get_or_create_user


def fake_message(text: str, user_id: int):
    return SimpleNamespace(
        text=text,
        from_user=SimpleNamespace(id=user_id, username="form", full_name="Form User"),
        answer=AsyncMock(),
    )


async def _reply(text: str, language: str = "en"):
    await init_db()
    async with SessionLocal() as session:
        await seed_defaults(session)
        user, _ = await get_or_create_user(session, 901, "intent", "Intent User")
        user.language = language
        await session.commit()
        return await route_message(session, user, text)


def test_intent_with_date_entity():
    reply = asyncio.run(_reply("I want to book an appointment on 2026-11-02"))
    assert reply.source == Source.INTENT and reply.intent == "book_appointment"
    assert reply.entities == {"date": "2026-11-02"}
    assert "2026-11-02" in reply.text


def test_khmer_intent():
    reply = asyncio.run(_reply("សួរ ខ្ញុំចង់ណាត់ជួប ថ្ងៃ 02/11/2026", language="km"))
    assert reply.intent == "book_appointment" and reply.entities["date"] == "2026-11-02"


def test_contact_intent_starts_the_form():
    reply = asyncio.run(_reply("Hello, I want to send a request please"))
    # "hello" is a rule, and rules come first
    assert reply.source == Source.RULE
    reply = asyncio.run(_reply("I want to send a request please"))
    assert reply.start_form and reply.intent == "contact_request"


def test_unrelated_text_is_not_an_intent():
    reply = asyncio.run(_reply("What are your opening hours?"))
    assert reply.source == Source.FAQ


def test_form_conversation_with_invalid_input_and_confirmation():
    uid = 902

    async def say(session, text):
        message = fake_message(text, uid)
        await handlers.on_text(message, session)
        return message.answer.call_args.args[0], message.answer.call_args.kwargs.get("reply_markup")

    async def scenario():
        await init_db()
        async with SessionLocal() as session:
            await seed_defaults(session)
            await handlers.cmd_start(fake_message("/start", uid), session)

            text, _ = await say(session, "I want to send a request")
            assert "Step 1/4" in text
            text, _ = await say(session, "R2")  # invalid name
            assert "real name" in text
            text, _ = await say(session, "Sok Dara")
            assert "Step 2/4" in text
            text, _ = await say(session, "123")  # invalid phone
            assert "not valid" in text
            text, _ = await say(session, "012 345 678")
            assert "Step 3/4" in text
            text, _ = await say(session, "dara@")  # invalid email
            assert "not valid" in text
            text, _ = await say(session, "dara@example.com")
            assert "Step 4/4" in text
            text, markup = await say(session, "I need my certificate")
            assert "Sok Dara" in text and "012345678" in text
            assert [b.callback_data for b in markup.inline_keyboard[0]] == ["form:yes", "form:no"]
            text, _ = await say(session, "maybe")  # not yes/no
            assert "Yes or No" in text
            text, _ = await say(session, "yes")
            assert "Thank you" in text

            user = (await session.execute(
                select(TelegramUser).where(TelegramUser.telegram_user_id == uid)
            )).scalar_one()
            conversation = (await session.execute(
                select(Conversation).where(Conversation.user_id == user.id)
            )).scalars().first()
            return user, conversation

    user, conversation = asyncio.run(scenario())
    assert (user.full_name, user.phone, user.email) == ("Sok Dara", "012345678", "dara@example.com")
    assert conversation.session_step is None
    assert conversation.support_status == SupportStatus.ASSIGNED  # auto-assigned to the seeded admin agent
    assert conversation.assigned_agent_id is not None
    assert conversation.context["request"]["request"] == "I need my certificate"


def test_form_can_be_cancelled():
    uid = 903

    async def scenario():
        await init_db()
        async with SessionLocal() as session:
            await seed_defaults(session)
            await handlers.on_menu_button(fake_message("📝 Send a Request", uid), session)
            await handlers.on_text(fake_message("Sok Dara", uid), session)
            cancel = fake_message("/cancel", uid)
            await handlers.cmd_cancel(cancel, session)
            after = fake_message("What are your opening hours?", uid)
            await handlers.on_text(after, session)  # normal routing again
            return cancel.answer.call_args.args[0], after.answer.call_args.args[0]

    cancelled, answer = asyncio.run(scenario())
    assert "cancelled" in cancelled
    assert "Monday" in answer
