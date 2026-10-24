"""Background jobs (APScheduler), run by the process that runs the bot.

  every 30 s   send scheduled broadcasts that are due
  every 10 min remind users who left a form unfinished for 30 minutes (once)
"""
import logging
from datetime import timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.db import SessionLocal
from app.i18n import t
from app.models import Conversation, TelegramUser, utcnow
from app.services import broadcast, logs
from app.services.notifications import NotificationType, notify

logger = logging.getLogger(__name__)
REMIND_AFTER = timedelta(minutes=30)


async def send_due_broadcasts() -> None:
    try:
        async with SessionLocal() as session:
            await broadcast.send_due(session)
    except Exception as exc:
        await logs.error("scheduled broadcast", exc)


async def send_form_reminders() -> int:
    """Reminder notification for a form left half-way (only one reminder per form)."""
    sent = 0
    try:
        async with SessionLocal() as session:
            rows = (await session.execute(
                select(Conversation, TelegramUser).join(TelegramUser, Conversation.user_id == TelegramUser.id)
                .where(Conversation.session_step.is_not(None), Conversation.status == "active",
                       Conversation.last_message_at <= utcnow() - REMIND_AFTER)
            )).all()
            for conversation, user in rows:
                if (conversation.context or {}).get("reminded"):
                    continue
                conversation.context = {**(conversation.context or {}), "reminded": True}
                await notify(session, user, NotificationType.REMINDER, t(user.language, "form_reminder"))
                sent += 1
    except Exception as exc:
        await logs.error("form reminders", exc)
    return sent


def build_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(send_due_broadcasts, "interval", seconds=30, id="broadcasts", max_instances=1)
    scheduler.add_job(send_form_reminders, "interval", minutes=10, id="reminders", max_instances=1)
    return scheduler
