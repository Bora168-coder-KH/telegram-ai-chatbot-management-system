"""Broadcast messages: audience, sending (throttled for Telegram limits) and scheduling."""
import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Broadcast, TelegramUser, UserStatus, utcnow
from app.services import logs
from app.services.notifications import NotificationType, notify

AUDIENCES = {
    "all": "All users",
    "active": "Active in the last 30 days",
    "en": "English users",
    "km": "Khmer users",
    "selected": "Selected users (IDs)",
}
SEND_DELAY = 0.05  # 20 messages per second, under Telegram's ~30 per second limit


def parse_ids(text: str) -> list[int]:
    """'1, 2 5' -> [1, 2, 5] (dashboard user IDs)."""
    return sorted({int(part) for part in text.replace(",", " ").split() if part.isdigit()})


def audience_query(audience: str, target_ids: list[int] | None = None):
    # Blocked and suspended users never receive broadcasts.
    query = select(TelegramUser).where(TelegramUser.status.in_([UserStatus.ACTIVE, UserStatus.INACTIVE]))
    if audience == "active":
        query = query.where(TelegramUser.last_interaction_at >= utcnow() - timedelta(days=30),
                            TelegramUser.status == UserStatus.ACTIVE)
    elif audience in ("en", "km"):
        query = query.where(TelegramUser.language == audience)
    elif audience == "selected":
        query = query.where(TelegramUser.id.in_(target_ids or []))
    return query.order_by(TelegramUser.id)


async def recipients(session: AsyncSession, audience: str, target_ids: list[int] | None = None) -> list[TelegramUser]:
    return list((await session.execute(audience_query(audience, target_ids))).scalars())


async def create(
    session: AsyncSession, message: str, audience: str, target_ids: list[int],
    scheduled_at: datetime | None, admin_id: int | None,
) -> Broadcast:
    if audience not in AUDIENCES:
        raise ValueError("unknown audience")
    if not message.strip():
        raise ValueError("the message is empty")
    broadcast = Broadcast(
        message=message.strip(), audience=audience, target_user_ids=target_ids if audience == "selected" else [],
        scheduled_at=scheduled_at, sent_by=admin_id, status="scheduled" if scheduled_at else "sending",
    )
    session.add(broadcast)
    await session.commit()
    return broadcast


async def send(session: AsyncSession, broadcast: Broadcast) -> dict:
    """Send to every recipient, one by one, and store the delivery result."""
    broadcast.status = "sending"
    await session.commit()
    users = await recipients(session, broadcast.audience, broadcast.target_user_ids)
    sent = failed = 0
    for user in users:
        notification = await notify(session, user, NotificationType.ANNOUNCEMENT, broadcast.message, broadcast.id)
        if notification.delivery_status == "sent":
            sent += 1
        else:
            failed += 1
        await asyncio.sleep(SEND_DELAY)
    broadcast.delivery_result = {"total": len(users), "sent": sent, "failed": failed}
    broadcast.sent_at = utcnow()
    broadcast.status = "sent"
    await session.commit()
    await logs.activity(session, "Broadcast sent", record_id=broadcast.id,
                        details=f"{sent} sent, {failed} failed of {len(users)}")
    return broadcast.delivery_result


async def send_due(session: AsyncSession) -> int:
    """Scheduler job: send scheduled broadcasts whose time has come."""
    due = (await session.execute(
        select(Broadcast).where(Broadcast.status == "scheduled", Broadcast.scheduled_at <= utcnow())
    )).scalars().all()
    for broadcast in due:
        await send(session, broadcast)
    return len(due)
