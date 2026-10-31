"""Activity, Audit and Error logs."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from sqlalchemy import select

from app.bot import handlers
from app.db import SessionLocal, init_db
from app.models import Log
from app.seed import seed_defaults
from app.services import logs


def _logs(log_type: str):
    async def run():
        async with SessionLocal() as session:
            return (await session.execute(select(Log).where(Log.log_type == log_type))).scalars().all()
    return asyncio.run(run())


def test_new_user_writes_activity_log():
    async def scenario():
        await init_db()
        async with SessionLocal() as session:
            await seed_defaults(session)
            message = SimpleNamespace(text="/start", answer=AsyncMock(),
                                      from_user=SimpleNamespace(id=7001, username="logme", full_name="Log Me"))
            await handlers.cmd_start(message, session)
    asyncio.run(scenario())
    assert any(log.action == "New Telegram user" and log.record_id for log in _logs(logs.LogType.ACTIVITY))


def test_audit_and_error_logs():
    async def scenario():
        await init_db()
        async with SessionLocal() as session:
            await logs.audit(session, "admin@example.com", "Deleted FAQ", record_id=42)
        try:
            raise ValueError("boom")
        except ValueError as exc:
            await logs.error("unit test", exc)
    asyncio.run(scenario())
    assert any(log.actor == "admin@example.com" and log.record_id == 42 for log in _logs(logs.LogType.AUDIT))
    assert any("ValueError: boom" in log.details for log in _logs(logs.LogType.ERROR))


def test_bot_error_handler_logs_and_answers(monkeypatch):
    monkeypatch.setattr(handlers, "Message", SimpleNamespace)  # pass the isinstance check
    message = SimpleNamespace(answer=AsyncMock())
    event = SimpleNamespace(exception=RuntimeError("handler crashed"),
                            update=SimpleNamespace(update_id=99, message=message, callback_query=None))
    asyncio.run(init_db())
    assert asyncio.run(handlers.on_error(event)) is True
    assert "something went wrong" in message.answer.call_args.args[0]
    assert any("handler crashed" in log.details for log in _logs(logs.LogType.ERROR))
