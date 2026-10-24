"""Human handoff: support requests, the agent queue and status changes."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Conversation, SupportStatus, utcnow


async def request_human_support(session: AsyncSession, conversation: Conversation, note: str = "") -> None:
    """Mark the conversation as an open support request (it enters the agent queue)."""
    if conversation.support_status in (None, SupportStatus.RESOLVED, SupportStatus.CLOSED):
        conversation.support_status = SupportStatus.OPEN
        conversation.assigned_agent_id = None
        conversation.handoff_requested_at = utcnow()
    if note:
        conversation.context = {**(conversation.context or {}), "handoff_note": note}
    await session.commit()
