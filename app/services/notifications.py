"""Notifications to Telegram users (welcome, reminder, support reply, status, announcement).

Every notification is stored in the `notifications` table with its delivery status.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification, TelegramUser, utcnow
from app.services import logs, telegram


class NotificationType:
    WELCOME, REMINDER, SUPPORT_REPLY, STATUS, ANNOUNCEMENT = (
        "Welcome", "Reminder", "Support Reply", "Status Update", "Announcement",
    )


def record(
    session: AsyncSession, user: TelegramUser, kind: str, content: str,
    delivered: bool = True, broadcast_id: int | None = None,
) -> Notification:
    """Store a notification that was already sent (e.g. by a bot handler)."""
    notification = Notification(
        user_id=user.id, type=kind, content=content, broadcast_id=broadcast_id,
        sent_at=utcnow() if delivered else None, delivery_status="sent" if delivered else "failed",
    )
    session.add(notification)
    return notification


async def notify(
    session: AsyncSession, user: TelegramUser, kind: str, content: str, broadcast_id: int | None = None,
) -> Notification:
    """Send a message to the user through Telegram and store the result."""
    delivered, error = await telegram.send_text(user.telegram_user_id, content)
    notification = record(session, user, kind, content, delivered, broadcast_id)
    if error:
        await logs.error(f"{kind} notification to user {user.id}", details=error)
    await session.commit()
    return notification
