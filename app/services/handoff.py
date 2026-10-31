"""Human handoff: support requests, the agent queue and status changes.

    Open -> Assigned -> In Progress -> Resolved -> Closed

  Open         the user asked for a human; the request waits in the agent queue
  Assigned     an agent took it (or it was auto-assigned to an available agent)
  In Progress  the agent replied; the bot stops auto-answering this conversation
  Resolved     the agent solved it; the user is asked to rate the support
  Closed       finished; the user's next message starts a new conversation
A Resolved or Closed request can be reopened (back to Open).
"""
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.i18n import t
from app.models import Admin, Agent, Conversation, Message, Source, SupportStatus, TelegramUser, utcnow
from app.services import logs
from app.services.notifications import NotificationType, notify

S = SupportStatus
ACTIVE = (S.OPEN, S.ASSIGNED, S.IN_PROGRESS)
ALL = (S.OPEN, S.ASSIGNED, S.IN_PROGRESS, S.RESOLVED, S.CLOSED)
TRANSITIONS = {
    S.OPEN: {S.ASSIGNED, S.CLOSED},
    S.ASSIGNED: {S.OPEN, S.IN_PROGRESS, S.RESOLVED, S.CLOSED},
    S.IN_PROGRESS: {S.OPEN, S.RESOLVED, S.CLOSED},
    S.RESOLVED: {S.OPEN, S.CLOSED},
    S.CLOSED: {S.OPEN},
}


def human_mode(conversation: Conversation) -> bool:
    """An agent is handling this conversation: the bot only stores the user's messages."""
    return conversation.support_status in (S.ASSIGNED, S.IN_PROGRESS)


async def active_load(session: AsyncSession, agent_id: int) -> int:
    query = select(func.count(Conversation.id)).where(
        Conversation.assigned_agent_id == agent_id, Conversation.support_status.in_(ACTIVE)
    )
    return (await session.execute(query)).scalar_one()


async def pick_agent(session: AsyncSession) -> Agent | None:
    """The available agent with the fewest active requests."""
    agents = (await session.execute(
        select(Agent).join(Admin).where(Agent.availability == "available", Admin.status == "Active")
        .order_by(Agent.id)
    )).scalars().all()
    best, best_load = None, None
    for agent in agents:
        load = await active_load(session, agent.id)
        if best_load is None or load < best_load:
            best, best_load = agent, load
    return best


async def request_human_support(
    session: AsyncSession, conversation: Conversation, note: str = "", auto_assign: bool = True,
) -> None:
    """Open a support request (it enters the agent queue), and auto-assign it if an agent is free."""
    if conversation.support_status not in ACTIVE:
        conversation.support_status = S.OPEN
        conversation.status = "active"
        conversation.assigned_agent_id = None
        conversation.handoff_requested_at = utcnow()
        conversation.resolution_status = "unresolved"
        await logs.conversation_log(session, "Support requested", record_id=conversation.id,
                                    details=note, commit=False)
    if note:
        conversation.context = {**(conversation.context or {}), "handoff_note": note}
    await session.commit()
    if auto_assign and conversation.support_status == S.OPEN:
        agent = await pick_agent(session)
        if agent:
            await assign(session, conversation, agent, actor="auto-assign")


async def assign(session: AsyncSession, conversation: Conversation, agent: Agent, actor: str) -> None:
    conversation.assigned_agent_id = agent.id
    if conversation.support_status in (None, S.OPEN):
        conversation.support_status = S.ASSIGNED
    await logs.conversation_log(session, "Agent assigned", actor=actor, record_id=conversation.id,
                                details=f"agent {agent.id}", commit=False)
    await session.commit()


async def change_status(session: AsyncSession, conversation: Conversation, status: str, actor: str) -> None:
    """Move a support request to another status. Raises ValueError for a change that is not allowed."""
    current = conversation.support_status
    if current is None or status not in TRANSITIONS.get(current, set()):
        raise ValueError(f"Cannot change status from {current} to {status}")
    conversation.support_status = status
    user = await session.get(TelegramUser, conversation.user_id)
    if status == S.OPEN:
        conversation.assigned_agent_id = None
        conversation.status = "active"
        conversation.resolution_status = "unresolved"
    elif status == S.RESOLVED:
        conversation.resolution_status = "resolved"
    elif status == S.CLOSED:
        conversation.status = "closed"  # the next message starts a new conversation
    await logs.conversation_log(session, f"Status {current} -> {status}", actor=actor,
                                record_id=conversation.id, commit=False)
    await session.commit()
    if user and status in (S.RESOLVED, S.CLOSED):
        await notify(session, user, NotificationType.STATUS, t(user.language, f"support_{status.lower()}"))


@dataclass
class ReplyResult:
    message: Message
    delivered: bool


async def agent_reply(
    session: AsyncSession, conversation: Conversation, agent: Agent | None, text: str, actor: str,
) -> ReplyResult:
    """An agent answers from the dashboard: store it, send it to the user, move the status on."""
    user = await session.get(TelegramUser, conversation.user_id)
    if user is None:
        raise ValueError("conversation has no user")
    if conversation.support_status in (None, S.RESOLVED, S.CLOSED):
        # the agent started the conversation from the dashboard
        conversation.support_status, conversation.status = S.OPEN, "active"
        conversation.handoff_requested_at = conversation.handoff_requested_at or utcnow()
    if agent and conversation.assigned_agent_id is None:
        conversation.assigned_agent_id = agent.id
    conversation.support_status = S.IN_PROGRESS
    message = Message(
        conversation_id=conversation.id, user_id=user.id, direction="outgoing", content=text,
        response_source=Source.AGENT, agent_id=agent.id if agent else None,
    )
    conversation.last_message_at = utcnow()
    session.add(message)
    await session.commit()
    notification = await notify(session, user, NotificationType.SUPPORT_REPLY, text)
    await logs.conversation_log(session, "Agent replied", actor=actor, record_id=conversation.id)
    return ReplyResult(message, notification.delivery_status == "sent")


async def queue(session: AsyncSession, statuses: tuple[str, ...] = ACTIVE) -> list[Conversation]:
    """Support requests, oldest first (the agent queue)."""
    result = await session.execute(
        select(Conversation)
        .where(Conversation.support_status.in_(statuses))
        .order_by(Conversation.handoff_requested_at.asc(), Conversation.id.asc())
        .options(selectinload(Conversation.user), selectinload(Conversation.agent).selectinload(Agent.admin))
    )
    return list(result.scalars())
