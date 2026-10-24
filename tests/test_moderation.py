"""Rate limit, spam detection and content moderation."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from sqlalchemy import select

from app.bot import middlewares
from app.db import SessionLocal, init_db
from app.models import TelegramUser, UserStatus
from app.services import moderation
from app.services.moderation import RATE_LIMIT, Guard
from app.services.users import get_or_create_user


def test_rate_limit_warns_once():
    guard = Guard()
    verdicts = [guard.check(1, f"question {i}", now=i * 0.1) for i in range(RATE_LIMIT + 3)]
    assert all(v.allowed for v in verdicts[:RATE_LIMIT])
    blocked = verdicts[RATE_LIMIT:]
    assert all(v.reason == "rate_limit" for v in blocked)
    assert [v.notify for v in blocked] == [True, False, False]
    assert guard.check(1, "later", now=100).allowed  # the window has passed


def test_repeated_message_and_links_are_spam():
    guard = Guard()
    assert guard.check(2, "buy now", now=0).allowed
    assert guard.check(2, "Buy now!", now=5).allowed
    assert guard.check(2, "buy now", now=10).reason == "spam"
    links = "see https://a.com https://b.com www.c.com t.me/d"
    assert Guard().check(3, links, now=0).reason == "spam"


def test_too_many_spam_strikes_suspends():
    guard = Guard()
    verdicts = [guard.check(4, "same", now=i * 20) for i in range(5)]
    assert [v.suspend for v in verdicts if not v.allowed] == [False, False, True]


def test_blocked_words():
    guard = Guard()
    assert guard.check(5, "this is shit", now=0).reason == "moderation"
    assert guard.check(5, "អាឆ្កួត", now=1).reason == "moderation"
    assert guard.check(5, "Shitake mushrooms?", now=2).allowed  # whole words only for English


def test_middleware_blocks_and_suspends(monkeypatch):
    monkeypatch.setattr(moderation, "guard", Guard())
    monkeypatch.setattr(middlewares, "guard", moderation.guard)
    monkeypatch.setattr(middlewares, "Message", SimpleNamespace)

    async def scenario():
        await init_db()
        async with SessionLocal() as session:
            await get_or_create_user(session, 6601, "spammer", "Spam Mer")
            handler = AsyncMock()
            replies = []
            for _ in range(5):
                event = SimpleNamespace(text="spam spam", caption=None, answer=AsyncMock(),
                                        from_user=SimpleNamespace(id=6601))
                await middlewares.ProtectionMiddleware()(handler, event, {"session": session})
                replies.append(event.answer.call_args.args[0] if event.answer.called else None)
            user = (await session.execute(select(TelegramUser).where(TelegramUser.telegram_user_id == 6601))).scalar_one()
            return handler.await_count, replies, user.status
    calls, replies, status = asyncio.run(scenario())
    assert calls == 2  # the first two messages reach the bot
    assert "same message" in replies[2] and "suspended" in replies[4]
    assert status == UserStatus.SUSPENDED
