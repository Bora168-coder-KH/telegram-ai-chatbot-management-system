"""User, conversation and message storage helpers."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Conversation, Message, SupportStatus, TelegramUser, utcnow


async def get_or_create_user(
    session: AsyncSession, telegram_id: int, username: str | None, full_name: str
) -> tuple[TelegramUser, bool]:
    """Register a Telegram user on first contact. Returns (user, created)."""
    result = await session.execute(
        select(TelegramUser).where(TelegramUser.telegram_user_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    created = user is None
    if created:
        user = TelegramUser(
            telegram_user_id=telegram_id,
            username=username,
            full_name=full_name,
            language=settings.default_language,
        )
        session.add(user)
    else:
        user.username = username
        user.full_name = full_name
        user.last_interaction_at = utcnow()
    await session.commit()
    return user, created


async def get_open_conversation(session: AsyncSession, user: TelegramUser) -> Conversation:
    """Return the user's active conversation, or start a new one."""
    result = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user.id, Conversation.status == "active")
        .order_by(Conversation.id.desc())
    )
    conversation = result.scalars().first()
    if conversation is None:
        conversation = Conversation(user_id=user.id)
        session.add(conversation)
        await session.commit()
    return conversation


async def save_message(
    session: AsyncSession,
    conversation: Conversation,
    user: TelegramUser,
    direction: str,
    content: str,
    message_type: str = "text",
    source: str | None = None,
) -> Message:
    message = Message(
        conversation_id=conversation.id,
        user_id=user.id,
        direction=direction,
        message_type=message_type,
        content=content,
        response_source=source,
    )
    conversation.last_message_at = utcnow()
    session.add(message)
    await session.commit()
    return message


async def request_human_support(session: AsyncSession, conversation: Conversation) -> None:
    """Human handoff, step 1: mark the conversation as an open support request.

    TODO (team task): assign an agent, notify agents, let agents reply from the dashboard.
    """
    conversation.support_status = SupportStatus.OPEN
    await session.commit()
