"""Webhook mode: Telegram sends updates to the dashboard instead of the bot polling for them.

Set in .env:
    BOT_MODE=webhook
    WEBHOOK_URL=https://your-domain.example      (public HTTPS address of the dashboard)
    WEBHOOK_SECRET=<a long random string>
Then run only:  uvicorn app.web.main:app
The dashboard registers  WEBHOOK_URL/telegram/webhook  with Telegram on start-up,
checks the secret header on every update, and runs the scheduler itself.
"""
import logging
import secrets

from aiogram import Bot, Dispatcher
from fastapi import APIRouter, HTTPException, Request

from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
WEBHOOK_PATH = "/telegram/webhook"


class WebhookState:
    bot: Bot | None = None
    dispatcher: Dispatcher | None = None
    scheduler = None


state = WebhookState()


def enabled() -> bool:
    return settings.bot_mode == "webhook"


async def start() -> None:
    from app.bot.runtime import build_dispatcher, prepare_bot
    from app.services.scheduler import build_scheduler

    if not (settings.bot_token and settings.webhook_url and settings.webhook_secret):
        raise SystemExit("Webhook mode needs BOT_TOKEN, WEBHOOK_URL and WEBHOOK_SECRET in .env")
    state.bot = await prepare_bot()
    state.dispatcher = build_dispatcher()
    url = settings.webhook_url.rstrip("/") + WEBHOOK_PATH
    await state.bot.set_webhook(url, secret_token=settings.webhook_secret,
                                allowed_updates=state.dispatcher.resolve_used_update_types())
    logger.info("Webhook set to %s", url)
    state.scheduler = build_scheduler()
    state.scheduler.start()


async def stop() -> None:
    if state.scheduler:
        state.scheduler.shutdown(wait=False)
    if state.bot:
        await state.bot.session.close()  # the webhook stays set, so updates queue at Telegram until restart


@router.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    if state.bot is None or state.dispatcher is None:
        raise HTTPException(404, "Webhook mode is off")
    sent = request.headers.get("x-telegram-bot-api-secret-token", "")
    if not secrets.compare_digest(sent, settings.webhook_secret):
        raise HTTPException(403, "Wrong secret")
    await state.dispatcher.feed_webhook_update(state.bot, await request.json())
    return {"ok": True}
