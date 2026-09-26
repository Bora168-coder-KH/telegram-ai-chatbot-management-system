"""Call the bot handlers with a fake Telegram message (no network needed)."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from sqlalchemy import select

from app.bot import handlers
from app.db import SessionLocal, init_db
from app.models import Feedback, Message as DbMessage, TelegramUser, UserStatus
from app.seed import seed_defaults


def fake_message(text: str, user_id: int = 222):
    return SimpleNamespace(
        text=text,
        from_user=SimpleNamespace(id=user_id, username="demo", full_name="Demo User"),
        answer=AsyncMock(),
    )


def test_start_then_question_then_menu_button():
    async def scenario():
        await init_db()
        async with SessionLocal() as session:
            await seed_defaults(session)

            # first /start -> language selection
            start = fake_message("/start")
            await handlers.cmd_start(start, session)
            assert "language" in start.answer.call_args.args[0].lower()

            # a known question -> FAQ answer
            question = fake_message("What are your opening hours?")
            await handlers.on_text(question, session)
            assert "Monday" in question.answer.call_args.args[0]

            # menu button "Contact"
            contact = fake_message("📞 Contact")
            await handlers.on_menu_button(contact, session)
            assert "support@example.com" in contact.answer.call_args.args[0]

            # unknown question -> fallback with buttons
            unknown = fake_message("zzz qqq www")
            await handlers.on_text(unknown, session)
            assert "did not understand" in unknown.answer.call_args.args[0]

            saved = (await session.execute(select(DbMessage))).scalars().all()
            return len(saved)

    assert asyncio.run(scenario()) >= 8  # incoming + outgoing messages were stored


def test_blocked_user_is_stopped():
    async def scenario():
        await init_db()
        async with SessionLocal() as session:
            await seed_defaults(session)
            first = fake_message("/menu", user_id=333)
            await handlers.cmd_menu(first, session)
            user = (await session.execute(
                select(TelegramUser).where(TelegramUser.telegram_user_id == 333)
            )).scalar_one()
            user.status = UserStatus.BLOCKED
            await session.commit()

            blocked = fake_message("hello", user_id=333)
            await handlers.on_text(blocked, session)
            return blocked.answer.call_args.args[0]

    assert "restricted" in asyncio.run(scenario())


def test_feedback_callback_saves_rating():
    async def scenario():
        await init_db()
        async with SessionLocal() as session:
            await seed_defaults(session)
            await handlers.on_text(fake_message("What are your opening hours?", user_id=444), session)
            callback = SimpleNamespace(
                data="fb:5:0",
                from_user=SimpleNamespace(id=444, username="demo", full_name="Demo User"),
                message=SimpleNamespace(edit_reply_markup=AsyncMock()),
                answer=AsyncMock(),
            )
            await handlers.on_feedback(callback, session)
            return (await session.execute(select(Feedback))).scalars().all()

    ratings = asyncio.run(scenario())
    assert any(r.rating == 5 for r in ratings)
