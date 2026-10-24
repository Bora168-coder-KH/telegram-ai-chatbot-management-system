"""Dashboard statistics, KPIs and chart data.

Resolution Rate - the team's definition
---------------------------------------
Counted per conversation, over conversations in which the user sent at least
one text message. Conversations with only button taps are left out.

A conversation is **Resolved** when either:
  (a) a support agent marked its support request Resolved or Closed after
      solving it (Conversation.resolution_status == "resolved"), or
  (b) it never needed a human (no support request), the bot's answer to the
      user's last question was not a fallback, and the user gave no negative
      feedback (rating 1 or 2) in that conversation.

Everything else is unresolved: the last answer was a fallback, the user rated
an answer badly, or a support request is still Open / Assigned / In Progress
(or was closed without being resolved).

Bot Answer Rate is the older message-level number: the share of incoming
questions that got a non-fallback answer.
"""
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.i18n import button_key
from app.models import (
    Conversation, Feedback, Message, Source, TelegramUser, UnknownQuestion, utcnow,
)
from app.services.text import normalize

ANSWER_SOURCES = [Source.COMMAND, Source.RULE, Source.INTENT, Source.FAQ, Source.KNOWLEDGE, Source.AI, Source.AGENT]
NEGATIVE_RATING = 2  # ratings 1-2 count as unhappy


async def _count(session: AsyncSession, query) -> int:
    return (await session.execute(query)).scalar_one() or 0


def _rate(part: int, total: int) -> float:
    return round(part / total * 100, 1) if total else 0.0


def is_resolved(conversation: Conversation, messages: list[Message], bad_feedback: bool) -> bool | None:
    """Apply the Resolution Rate definition above. None = not counted (no question asked)."""
    incoming = [m for m in messages if m.direction == "incoming" and m.message_type == "text"]
    if not incoming:
        return None
    if conversation.resolution_status == "resolved":
        return True  # (a) resolved by an agent
    if conversation.support_status is not None:
        return False  # a human was needed and has not resolved it
    last_question = incoming[-1]
    answers = [m for m in messages if m.direction == "outgoing" and m.id > last_question.id]
    if not answers or answers[0].response_source == Source.FALLBACK:
        return False
    return not bad_feedback  # (b) answered by the bot, nobody unhappy


async def resolution(session: AsyncSession, since: datetime | None = None, until: datetime | None = None) -> dict:
    """Resolved / counted conversations, using `is_resolved`."""
    query = select(Conversation)
    if since:
        query = query.where(Conversation.started_at >= since)
    if until:
        query = query.where(Conversation.started_at < until)
    conversations = (await session.execute(query)).scalars().all()
    ids = [c.id for c in conversations]
    by_conversation: dict[int, list[Message]] = defaultdict(list)
    bad: set[int] = set()
    if ids:
        for message in (await session.execute(
            select(Message).where(Message.conversation_id.in_(ids)).order_by(Message.id)
        )).scalars():
            by_conversation[message.conversation_id].append(message)
        bad = set((await session.execute(
            select(Feedback.conversation_id).where(
                Feedback.conversation_id.in_(ids), Feedback.rating <= NEGATIVE_RATING)
        )).scalars())
    counted = resolved = 0
    for conversation in conversations:
        result = is_resolved(conversation, by_conversation[conversation.id], conversation.id in bad)
        if result is None:
            continue
        counted += 1
        resolved += result
    return {"counted": counted, "resolved": resolved, "rate": _rate(resolved, counted)}


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
        session, select(func.count(Message.id)).where(Message.response_source.in_(ANSWER_SOURCES))
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
    resolved = await resolution(session)

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
        # KPIs (percent)
        "resolution_rate": resolved["rate"],  # see the module docstring
        "resolved_conversations": resolved["resolved"],
        "counted_conversations": resolved["counted"],
        "answer_rate": _rate(min(answered, questions), questions),
        "ai_answer_rate": _rate(ai_answers, questions),
        "fallback_rate": _rate(fallbacks, questions),
        "handoff_rate": _rate(handoffs, conversations),
        "satisfaction": round(float(avg_rating), 2) if avg_rating is not None else None,
    }


def _day(value: datetime) -> date:
    return value.date()


async def chart_data(session: AsyncSession, days: int = 14) -> dict:
    """Data for the dashboard charts (Chart.js): grouped in Python so it works on SQLite and PostgreSQL."""
    today = utcnow().date()
    labels = [today - timedelta(days=i) for i in range(days - 1, -1, -1)]
    start = datetime.combine(labels[0], datetime.min.time())

    users_before = await _count(
        session, select(func.count(TelegramUser.id)).where(TelegramUser.first_interaction_at < start)
    )
    joined = Counter(_day(d) for d in (await session.execute(
        select(TelegramUser.first_interaction_at).where(TelegramUser.first_interaction_at >= start)
    )).scalars())
    total, growth = users_before, []
    for day in labels:
        total += joined[day]
        growth.append(total)

    incoming, outgoing = Counter(), Counter()
    sources: Counter = Counter()
    questions: Counter = Counter()
    for created, direction, source, kind, content in (await session.execute(
        select(Message.created_at, Message.direction, Message.response_source, Message.message_type,
               Message.content).where(Message.created_at >= start)
    )).all():
        (incoming if direction == "incoming" else outgoing)[_day(created)] += 1
        if direction == "outgoing" and source:
            sources[source] += 1
        if (direction == "incoming" and kind == "text" and content and not content.startswith("/")
                and button_key(content) is None):
            questions[normalize(content)] += 1

    return {
        "labels": [d.strftime("%d %b") for d in labels],
        "new_users": [joined[d] for d in labels],
        "total_users": growth,
        "incoming": [incoming[d] for d in labels],
        "outgoing": [outgoing[d] for d in labels],
        "sources": dict(sources.most_common()),
        "popular_questions": [{"question": q, "count": n} for q, n in questions.most_common(8) if q],
    }
