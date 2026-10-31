"""Bot middlewares: a database session for every handler, and spam / abuse protection."""
from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy import select

from app.db import SessionLocal
from app.i18n import t
from app.models import TelegramUser, UserStatus
from app.services import logs
from app.services.moderation import guard


class DbSessionMiddleware(BaseMiddleware):
    """Gives every handler its own database session (`session` argument)."""

    async def __call__(self, handler, event, data):
        async with SessionLocal() as session:
            data["session"] = session
            return await handler(event, data)


class ProtectionMiddleware(BaseMiddleware):
    """Rate limit, spam detection and content moderation before any message handler runs."""

    async def __call__(self, handler, event, data):
        if not isinstance(event, Message) or event.from_user is None:
            return await handler(event, data)
        verdict = guard.check(event.from_user.id, event.text or event.caption)
        if verdict.allowed:
            return await handler(event, data)

        session = data["session"]
        user = (await session.execute(
            select(TelegramUser).where(TelegramUser.telegram_user_id == event.from_user.id)
        )).scalar_one_or_none()
        lang = user.language if user else "en"
        record_id = user.id if user else None
        if verdict.suspend and user and user.status == UserStatus.ACTIVE:
            user.status = UserStatus.SUSPENDED
            await logs.activity(session, "User suspended for spam", record_id=record_id)
            await event.answer(t(lang, "spam_suspended"))
            return None
        await logs.activity(session, f"Message blocked ({verdict.reason})", record_id=record_id)
        if verdict.notify:
            await event.answer(t(lang, verdict.reason))
        return None
