"""Webhook mode (Telegram is never called: the bot is a mock)."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.bot import runtime
from app.config import settings
from app.web import webhook
from app.web.main import app


@pytest.fixture
def webhook_mode(monkeypatch):
    bot = SimpleNamespace(set_webhook=AsyncMock(), session=SimpleNamespace(close=AsyncMock()))
    monkeypatch.setattr(settings, "bot_mode", "webhook")
    monkeypatch.setattr(settings, "bot_token", "123:fake")
    monkeypatch.setattr(settings, "webhook_url", "https://bot.example.com/")
    monkeypatch.setattr(settings, "webhook_secret", "s3cret")
    monkeypatch.setattr(runtime, "prepare_bot", AsyncMock(return_value=bot))
    yield bot
    webhook.state.bot = webhook.state.dispatcher = webhook.state.scheduler = None


def test_webhook_is_registered_and_checks_the_secret(webhook_mode, monkeypatch):
    with TestClient(app) as client:
        webhook_mode.set_webhook.assert_awaited_once()
        assert webhook_mode.set_webhook.call_args.args[0] == "https://bot.example.com/telegram/webhook"
        assert webhook_mode.set_webhook.call_args.kwargs["secret_token"] == "s3cret"

        feed = AsyncMock()
        monkeypatch.setattr(webhook.state.dispatcher, "feed_webhook_update", feed)
        update = {"update_id": 1, "message": {"message_id": 1, "date": 0, "chat": {"id": 1, "type": "private"},
                                              "text": "/start"}}
        assert client.post("/telegram/webhook", json=update).status_code == 403
        bad = client.post("/telegram/webhook", json=update, headers={"X-Telegram-Bot-Api-Secret-Token": "nope"})
        assert bad.status_code == 403
        ok = client.post("/telegram/webhook", json=update, headers={"X-Telegram-Bot-Api-Secret-Token": "s3cret"})
        assert ok.status_code == 200
        feed.assert_awaited_once_with(webhook_mode, update)
        assert webhook.state.scheduler.running
    webhook_mode.session.close.assert_awaited()


def test_webhook_route_is_off_in_polling_mode():
    with TestClient(app) as client:
        assert client.post("/telegram/webhook", json={}).status_code == 404


def test_webhook_mode_needs_settings(monkeypatch):
    monkeypatch.setattr(settings, "bot_token", "123:fake")
    monkeypatch.setattr(settings, "webhook_url", "")
    with pytest.raises(SystemExit, match="WEBHOOK_URL"):
        asyncio.run(webhook.start())
