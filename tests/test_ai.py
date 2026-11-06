"""AI provider client: prompt, retry and graceful failure (no network)."""
import asyncio
import json

import httpx

from app.config import settings
from app.db import init_db
from app.models import Bot
from app.services import ai


def _enable(monkeypatch):
    monkeypatch.setattr(settings, "ai_api_key", "test-key")
    monkeypatch.setattr(settings, "ai_model", "test/model")
    monkeypatch.setattr(ai.asyncio, "sleep", _no_sleep)


async def _no_sleep(_):
    return None


def _transport(responses: list):
    calls = []

    def handler(request: httpx.Request):
        calls.append(request)
        item = responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    return httpx.MockTransport(handler), calls


def _patch_client(monkeypatch, transport):
    real = httpx.AsyncClient
    monkeypatch.setattr(ai.httpx, "AsyncClient", lambda **kw: real(transport=transport, **kw))


def _ok(text: str):
    return httpx.Response(200, json={"choices": [{"message": {"content": text}}]})


def test_disabled_without_key():
    assert asyncio.run(ai.generate_answer("hi", "", "", "en")) is None


def test_prompt_has_language_style_and_context():
    messages = ai.build_messages("Refund?", "Refunds within 7 days.", "Be nice.", "km", "formal")
    system = messages[0]["content"]
    assert "Be nice." in system and "Khmer" in system and "formally" in system
    assert "Refunds within 7 days." in system
    assert messages[1] == {"role": "user", "content": "Refund?"}


def test_answer_after_retry(monkeypatch):
    _enable(monkeypatch)
    transport, calls = _transport([httpx.Response(503), httpx.ConnectTimeout("slow"), _ok("  Hello!  ")])
    _patch_client(monkeypatch, transport)
    bot = Bot(ai_model="custom/model", ai_temperature=0.1, ai_max_length=99, response_style="short")
    assert asyncio.run(ai.generate_answer("hi", "", "", "en", bot)) == "Hello!"
    assert len(calls) == 3
    body = json.loads(calls[-1].content)
    assert body["model"] == "custom/model" and body["max_tokens"] == 99
    assert calls[-1].headers["Authorization"] == "Bearer test-key"


def test_errors_return_none(monkeypatch):
    _enable(monkeypatch)
    transport, _ = _transport([httpx.Response(401, json={"error": "expired"})])
    _patch_client(monkeypatch, transport)
    asyncio.run(init_db())  # the failure is written to the Error log
    assert asyncio.run(ai.generate_answer("hi", "", "", "en")) is None

    transport, _ = _transport([_ok("   ")])  # empty answer
    _patch_client(monkeypatch, transport)
    assert asyncio.run(ai.generate_answer("hi", "", "", "en")) is None



def test_no_answer_marker_returns_none(monkeypatch):
    _enable(monkeypatch)
    for reply in ("NO_ANSWER", "NO_ANSWER.", "`NO_ANSWER`", " no_answer \n"):
        transport, _ = _transport([_ok(reply)])
        _patch_client(monkeypatch, transport)
        assert asyncio.run(ai.generate_answer("weather tomorrow?", "", "", "en")) is None, reply


def test_prompt_asks_for_no_answer_after_the_system_prompt():
    system = ai.build_messages("q", "", "If you are not sure, say so.", "en")[0]["content"]
    assert system.index("If you are not sure, say so.") < system.index(ai.NO_ANSWER)


def _route(text: str, language: str = "en"):
    from app.seed import seed_defaults
    from app.services.router import route_message
    from app.services.users import get_or_create_user
    from app.db import SessionLocal

    async def scenario():
        await init_db()
        async with SessionLocal() as session:
            await seed_defaults(session)
            user, _ = await get_or_create_user(session, 987654, "ai_tester", "AI Tester")
            user.language = language
            await session.commit()
            return await route_message(session, user, text)
    return asyncio.run(scenario())


def test_ai_answers_a_reworded_question_from_similar_faqs(monkeypatch):
    from app.models import Source

    _enable(monkeypatch)
    transport, calls = _transport([_ok("We are open Monday to Saturday.")])
    _patch_client(monkeypatch, transport)
    reply = _route("zq which days can I drop by your place")
    assert reply.source == Source.AI and reply.text == "We are open Monday to Saturday."
    system = json.loads(calls[0].content)["messages"][0]["content"]
    assert "Q: " in system and "A: " in system  # the closest FAQs were sent as context


def test_ai_no_answer_goes_to_fallback_with_human_support(monkeypatch):
    from sqlalchemy import select

    from app.db import SessionLocal
    from app.models import Source, UnknownQuestion

    _enable(monkeypatch)
    transport, _ = _transport([_ok("NO_ANSWER")])
    _patch_client(monkeypatch, transport)
    reply = _route("zq what is the weather on mars")
    assert reply.fallback and reply.source == Source.FALLBACK
    assert "Human Support" in reply.text

    async def saved():
        async with SessionLocal() as session:
            return [u.question for u in (await session.execute(select(UnknownQuestion))).scalars()]
    assert "zq what is the weather on mars" in asyncio.run(saved())


def test_ai_off_does_not_call_the_api(monkeypatch):
    from app.models import Source

    monkeypatch.setattr(settings, "ai_api_key", "")
    transport, calls = _transport([])
    _patch_client(monkeypatch, transport)
    assert _route("zq what is the weather on mars").source == Source.FALLBACK
    assert calls == []
