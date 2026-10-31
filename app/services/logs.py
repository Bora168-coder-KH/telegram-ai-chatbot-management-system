"""Activity, Audit, Conversation and Error logs (the `logs` table).

  Activity      something happened in the bot (new user, form sent, broadcast sent)
  Audit         an admin changed data (who, what, which record)
  Conversation  handoff and support status changes
  Error         an exception in the bot or a failed external call (AI, Telegram)
"""
import logging
import traceback

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal
from app.models import Log

logger = logging.getLogger(__name__)


class LogType:
    ACTIVITY, AUDIT, CONVERSATION, ERROR = "Activity", "Audit", "Conversation", "Error"


async def write_log(
    session: AsyncSession,
    log_type: str,
    action: str,
    actor: str = "system",
    record_id: int | None = None,
    details: str = "",
    commit: bool = True,
) -> Log:
    log = Log(log_type=log_type, actor=actor[:100], action=action[:200], record_id=record_id, details=details)
    session.add(log)
    if commit:
        await session.commit()
    return log


async def activity(session: AsyncSession, action: str, **kwargs) -> Log:
    return await write_log(session, LogType.ACTIVITY, action, **kwargs)


async def audit(session: AsyncSession, actor: str, action: str, record_id: int | None = None, details: str = "") -> Log:
    return await write_log(session, LogType.AUDIT, action, actor=actor, record_id=record_id, details=details)


async def conversation_log(session: AsyncSession, action: str, **kwargs) -> Log:
    return await write_log(session, LogType.CONVERSATION, action, **kwargs)


async def error(where: str, exc: BaseException | None = None, details: str = "") -> None:
    """Write an Error log in its own session, so a broken session cannot stop it."""
    if exc is not None:
        details = (details + "\n" if details else "") + "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        )[-4000:]
    try:
        async with SessionLocal() as session:
            await write_log(session, LogType.ERROR, where, details=details)
    except Exception:  # never let logging crash the caller
        logger.exception("could not write error log for %s", where)
