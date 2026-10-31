"""Retry logic for Telegram API errors."""
import asyncio
from unittest.mock import AsyncMock

import pytest
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError, TelegramRetryAfter
from aiogram.methods import SendMessage

from app.services import telegram

METHOD = SendMessage(chat_id=1, text="hi")


def _run(side_effect, attempts=4):
    make_request = AsyncMock(side_effect=side_effect)
    middleware = telegram.RetryMiddleware(attempts=attempts, base_delay=0)
    return make_request, asyncio.run(middleware(make_request, None, METHOD))


def test_network_error_is_retried(monkeypatch):
    monkeypatch.setattr(telegram.asyncio, "sleep", AsyncMock())
    make_request, result = _run([TelegramNetworkError(METHOD, "down"), TelegramNetworkError(METHOD, "down"), "ok"])
    assert result == "ok" and make_request.await_count == 3


def test_flood_limit_waits_retry_after(monkeypatch):
    sleep = AsyncMock()
    monkeypatch.setattr(telegram.asyncio, "sleep", sleep)
    _, result = _run([TelegramRetryAfter(METHOD, "flood", retry_after=5), "ok"])
    assert result == "ok"
    sleep.assert_awaited_once_with(5)


def test_bad_request_is_not_retried(monkeypatch):
    monkeypatch.setattr(telegram.asyncio, "sleep", AsyncMock())
    make_request = AsyncMock(side_effect=TelegramBadRequest(METHOD, "bad"))
    with pytest.raises(TelegramBadRequest):
        asyncio.run(telegram.RetryMiddleware(base_delay=0)(make_request, None, METHOD))
    assert make_request.await_count == 1


def test_gives_up_after_max_attempts(monkeypatch):
    monkeypatch.setattr(telegram.asyncio, "sleep", AsyncMock())
    make_request = AsyncMock(side_effect=TelegramNetworkError(METHOD, "down"))
    with pytest.raises(TelegramNetworkError):
        asyncio.run(telegram.RetryMiddleware(attempts=3, base_delay=0)(make_request, None, METHOD))
    assert make_request.await_count == 3


def test_send_text_without_token():
    assert asyncio.run(telegram.send_text(1, "hi")) == (False, "BOT_TOKEN is not set")
