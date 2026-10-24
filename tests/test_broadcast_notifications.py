"""Broadcasts (audience, throttled sending, schedule) and notifications (welcome, reminder)."""
import asyncio
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock

from sqlalchemy import select

from app.bot import handlers
from app.db import SessionLocal, init_db
from app.models import Broadcast, Conversation, Notification, TelegramUser, UserStatus, utcnow
from app.seed import seed_defaults
from app.services import broadcast, scheduler, telegram
from app.services.users import get_or_create_user


def _fake_bot(monkeypatch):
    bot = SimpleNamespace(send_message=AsyncMock())
    monkeypatch.setattr(telegram, "get_bot", lambda: bot)
    monkeypatch.setattr(broadcast, "SEND_DELAY", 0)
    return bot


async def _users(session):
    a, _ = await get_or_create_user(session, 9101, "en_user", "English User")
    b, _ = await get_or_create_user(session, 9102, "km_user", "Khmer User")
    c, _ = await get_or_create_user(session, 9103, "blocked", "Blocked User")
    b.language, c.status = "km", UserStatus.BLOCKED
    await session.commit()
    return a, b, c


def test_parse_ids():
    assert broadcast.parse_ids("3, 1 2,,x 3") == [1, 2, 3]


def test_audience_never_includes_blocked_users():
    async def scenario():
        await init_db()
        async with SessionLocal() as session:
            a, b, c = await _users(session)
            everyone = {u.id for u in await broadcast.recipients(session, "all")}
            khmer = {u.id for u in await broadcast.recipients(session, "km")}
            chosen = {u.id for u in await broadcast.recipients(session, "selected", [a.id, c.id])}
            return a, b, c, everyone, khmer, chosen
    a, b, c, everyone, khmer, chosen = asyncio.run(scenario())
    assert a.id in everyone and b.id in everyone and c.id not in everyone
    assert b.id in khmer and a.id not in khmer
    assert chosen == {a.id}


def test_send_now_and_scheduled(monkeypatch):
    bot = _fake_bot(monkeypatch)

    async def scenario():
        await init_db()
        async with SessionLocal() as session:
            a, b, _ = await _users(session)
            now = await broadcast.create(session, "Hello everyone", "selected", [a.id, b.id], None, None)
            result = await broadcast.send(session, now)
            later = await broadcast.create(session, "Exam tomorrow", "selected", [a.id],
                                           utcnow() + timedelta(hours=1), None)
            not_yet = await broadcast.send_due(session)
            later.scheduled_at = utcnow() - timedelta(minutes=1)
            await session.commit()
            due = await broadcast.send_due(session)
            await session.refresh(later)
            count = len((await session.execute(
                select(Notification).where(Notification.broadcast_id == now.id))).scalars().all())
            return result, not_yet, due, later.status, count
    result, not_yet, due, status, count = asyncio.run(scenario())
    assert result == {"total": 2, "sent": 2, "failed": 0} and count == 2
    assert (not_yet, due, status) == (0, 1, "sent")
    assert bot.send_message.await_count == 3


def test_welcome_and_form_reminder(monkeypatch):
    bot = _fake_bot(monkeypatch)
    monkeypatch.setattr(handlers, "Message", SimpleNamespace)
    uid = 9201

    async def scenario():
        await init_db()
        async with SessionLocal() as session:
            await seed_defaults(session)
            from_user = SimpleNamespace(id=uid, username="w", full_name="Welcome User")
            await handlers.cmd_start(SimpleNamespace(text="/start", from_user=from_user, answer=AsyncMock()), session)
            callback = SimpleNamespace(data="lang:en", from_user=from_user, answer=AsyncMock(),
                                       message=SimpleNamespace(edit_reply_markup=AsyncMock(), answer=AsyncMock()))
            await handlers.on_language(callback, session)
            await handlers.on_menu_button(SimpleNamespace(text="📝 Send a Request", from_user=from_user,
                                                          answer=AsyncMock()), session)
            user = (await session.execute(select(TelegramUser).where(TelegramUser.telegram_user_id == uid))).scalar_one()
            conversation = (await session.execute(select(Conversation).where(Conversation.user_id == user.id))).scalar_one()
            conversation.last_message_at = utcnow() - timedelta(hours=1)
            await session.commit()
            user_id = user.id
        first = await scheduler.send_form_reminders()
        second = await scheduler.send_form_reminders()  # only one reminder per form
        async with SessionLocal() as session:
            kinds = (await session.execute(select(Notification.type).where(Notification.user_id == user_id))).scalars().all()
        return first, second, kinds
    first, second, kinds = asyncio.run(scenario())
    assert (first, second) == (1, 0)
    assert sorted(kinds) == ["Reminder", "Welcome"]
    assert "not finished" in bot.send_message.call_args.args[1]
