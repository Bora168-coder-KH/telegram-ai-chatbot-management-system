"""Dashboard statistics and KPIs."""
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Conversation, Feedback, Message, Source, TelegramUser, UnknownQuestion, utcnow,
)


async def _count(session: AsyncSession, query) -> int:
    return (await session.execute(query)).scalar_one() or 0


def _rate(part: int, total: int) -> float:
    return round(part / total * 100, 1) if total else 0.0


async def dashboard_stats(session: AsyncSession) -> dict:
    now = utcnow()
    day_ago, week_ago = now - timedelta(days=1), now - timedelta(days=7)

    total_users = await _count(session, select(func.count(TelegramUser.id)))
    new_users = await _count(
        session, select(func.count(TelegramUser.id)).where(TelegramUser.first_interaction_at >= day_ago)
    )
    active_users = await _count(
        session, select(func.count(TelegramUser.id)).where(TelegramUser.last_interaction_at >= week_ago)
    )

    incoming = await _count(session, select(func.count(Message.id)).where(Message.direction == "incoming"))
    outgoing = await _count(session, select(func.count(Message.id)).where(Message.direction == "outgoing"))
    questions = await _count(
        session,
        select(func.count(Message.id)).where(Message.direction == "incoming", Message.message_type == "text"),
    )

    def by_source(source: str):
        return select(func.count(Message.id)).where(Message.response_source == source)

    ai_answers = await _count(session, by_source(Source.AI))
    fallbacks = await _count(session, by_source(Source.FALLBACK))
    answered = await _count(
        session,
        select(func.count(Message.id)).where(
            Message.response_source.in_([Source.COMMAND, Source.RULE, Source.FAQ, Source.KNOWLEDGE, Source.AI])
        ),
    )

    conversations = await _count(session, select(func.count(Conversation.id)))
    active_conversations = await _count(
        session, select(func.count(Conversation.id)).where(Conversation.status == "active")
    )
    handoffs = await _count(
        session, select(func.count(Conversation.id)).where(Conversation.support_status.is_not(None))
    )
    unanswered = await _count(
        session, select(func.count(UnknownQuestion.id)).where(UnknownQuestion.status == "open")
    )
    avg_rating = (await session.execute(select(func.avg(Feedback.rating)))).scalar_one()

    return {
        "total_users": total_users,
        "new_users": new_users,
        "active_users": active_users,
        "total_messages": incoming + outgoing,
        "incoming": incoming,
        "outgoing": outgoing,
        "conversations": conversations,
        "active_conversations": active_conversations,
        "unanswered": unanswered,
        "ai_requests": ai_answers,
        "handoffs": handoffs,
        # KPIs (percent). Resolution Rate here = questions answered by a non-fallback source.
        "resolution_rate": _rate(answered, questions),
        "ai_answer_rate": _rate(ai_answers, questions),
        "fallback_rate": _rate(fallbacks, questions),
        "handoff_rate": _rate(handoffs, conversations),
        "satisfaction": round(float(avg_rating), 2) if avg_rating is not None else None,
    }
