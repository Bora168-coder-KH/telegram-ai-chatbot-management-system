"""Human handoff: queue, assignment, status changes, agent reply, bot silence in human mode."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select

from app.bot import handlers
from app.db import SessionLocal, init_db
from app.models import Agent, Conversation, Message, Notification, Source, SupportStatus as S, TelegramUser
from app.seed import seed_defaults
from app.services import handoff, telegram


def fake_message(text: str, user_id: int):
    return SimpleNamespace(text=text, answer=AsyncMock(),
                           from_user=SimpleNamespace(id=user_id, username="h", full_name="Handoff User"))


async def _conversation(session, user_id: int) -> Conversation:
    user = (await session.execute(
        select(TelegramUser).where(TelegramUser.telegram_user_id == user_id))).scalar_one()
    return (await session.execute(
        select(Conversation).where(Conversation.user_id == user.id).order_by(Conversation.id.desc())
    )).scalars().first()


def test_full_handoff_flow(monkeypatch):
    bot = SimpleNamespace(send_message=AsyncMock())
    monkeypatch.setattr(telegram, "get_bot", lambda: bot)
    uid = 8001

    async def scenario():
        await init_db()
        async with SessionLocal() as session:
            await seed_defaults(session)
            agent = (await session.execute(select(Agent))).scalars().first()
            agent.availability = "away"  # nobody free: the request waits in the queue
            await session.commit()

            await handlers.on_menu_button(fake_message("🧑‍💼 Human Support", uid), session)
            conversation = await _conversation(session, uid)
            assert conversation.support_status == S.OPEN
            assert conversation.id in [c.id for c in await handoff.queue(session)]

            await handoff.assign(session, conversation, agent, actor="admin")
            assert conversation.support_status == S.ASSIGNED

            # while an agent handles it, the bot does not auto-answer (only says "passed to the agent" once)
            first, second = fake_message("What are your opening hours?", uid), fake_message("hello?", uid)
            await handlers.on_text(first, session)
            await handlers.on_text(second, session)
            assert "passed to the support agent" in first.answer.call_args.args[0]
            second.answer.assert_not_called()

            result = await handoff.agent_reply(session, conversation, agent, "Hi, I am Dara from support.", "admin")
            assert result.delivered and conversation.support_status == S.IN_PROGRESS
            bot.send_message.assert_awaited_with(conversation.user.telegram_user_id, "Hi, I am Dara from support.")
            saved = await session.get(Message, result.message.id)
            assert saved.response_source == Source.AGENT and saved.agent_id == agent.id

            await handoff.change_status(session, conversation, S.RESOLVED, actor="admin")
            assert conversation.resolution_status == "resolved"
            await handoff.change_status(session, conversation, S.CLOSED, actor="admin")
            assert conversation.status == "closed"

            kinds = (await session.execute(
                select(Notification.type).where(Notification.user_id == conversation.user_id))).scalars().all()
            assert {"Support Reply", "Status Update"} <= set(kinds)

            # after closing, a new message starts a new conversation that the bot answers again
            again = fake_message("What are your opening hours?", uid)
            await handlers.on_text(again, session)
            assert "Monday" in again.answer.call_args.args[0]
            assert (await _conversation(session, uid)).id != conversation.id

    asyncio.run(scenario())


def test_invalid_status_change_is_refused():
    async def scenario():
        await init_db()
        async with SessionLocal() as session:
            await seed_defaults(session)
            await handlers.on_menu_button(fake_message("🧑‍💼 Human Support", 8002), session)
            conversation = await _conversation(session, 8002)
            with pytest.raises(ValueError):
                await handoff.change_status(session, conversation, S.IN_PROGRESS, actor="admin")
    asyncio.run(scenario())


def test_auto_assign_picks_least_busy_agent():
    async def scenario():
        await init_db()
        async with SessionLocal() as session:
            await seed_defaults(session)
            for agent in (await session.execute(select(Agent))).scalars():
                agent.availability = "available"
            await session.commit()
            await handlers.on_menu_button(fake_message("🧑‍💼 Human Support", 8003), session)
            conversation = await _conversation(session, 8003)
            return conversation.support_status, conversation.assigned_agent_id
    status, agent_id = asyncio.run(scenario())
    assert status == S.ASSIGNED and agent_id is not None
