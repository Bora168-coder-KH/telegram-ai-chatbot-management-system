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

