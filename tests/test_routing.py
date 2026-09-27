"""Tests for the Response Routing Logic (Rule -> FAQ -> Knowledge Base -> Fallback)."""
import asyncio

from sqlalchemy import select

from app.db import SessionLocal, init_db
from app.models import Source, UnknownQuestion
from app.seed import seed_defaults
from app.services.router import normalize, route_message
from app.services.users import get_or_create_user


def run(coro):
    return asyncio.run(coro)


async def _reply(text: str, language: str = "en"):
    await init_db()
    async with SessionLocal() as session:
        await seed_defaults(session)
        user, _ = await get_or_create_user(session, 111, "tester", "Test User")
        user.language = language
        await session.commit()
        return await route_message(session, user, text)


def test_normalize():
    assert normalize("  Hello,   WORLD!! ") == "hello world"


def test_keyword_rule():
    reply = run(_reply("hello there"))
    assert reply.source == Source.RULE


def test_rule_does_not_match_inside_words():
    # "hi" must not match inside "this"
    reply = run(_reply("this is unrelated zzz"))
    assert reply.source != Source.RULE


def test_faq_exact_question():
    reply = run(_reply("What are your opening hours?"))
    assert reply.source == Source.FAQ
    assert "Monday" in reply.text


def test_faq_keyword():
    reply = run(_reply("when do you open, what are the office hours"))
    assert reply.source == Source.FAQ


def test_faq_khmer():
    reply = run(_reply("ម៉ោងបើកទ្វាររបស់អ្នកគឺម៉ោងប៉ុន្មាន?", language="km"))
    assert reply.source == Source.FAQ


def test_knowledge_base():
    reply = run(_reply("can I get a refund?"))
    assert reply.source == Source.KNOWLEDGE


def test_fallback_saves_unknown_question():
    async def scenario():
        reply = await _reply("blorp quantum zebra")
        async with SessionLocal() as session:
            rows = (await session.execute(select(UnknownQuestion))).scalars().all()
        return reply, rows

    reply, rows = run(scenario())
    assert reply.fallback and reply.source == Source.FALLBACK
    assert any(r.question == "blorp quantum zebra" for r in rows)
