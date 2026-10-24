"""Sending to Telegram from outside a handler (agent replies, broadcasts, reminders).

Retry logic for Telegram API errors lives in `RetryMiddleware`, which is added to
every Bot this app creates (the polling bot too), so all API calls get it:
  - 429 Too Many Requests: wait the `retry_after` seconds Telegram asks for
  - network errors and 5xx server errors: retry with backoff (1s, 2s, 4s)
  - other errors (bad request, user blocked the bot): no retry
"""
import asyncio
import logging

from aiogram import Bot
from aiogram.client.session.middlewares.base import BaseRequestMiddleware
from aiogram.exceptions import (
    TelegramAPIError, TelegramForbiddenError, TelegramNetworkError, TelegramRetryAfter, TelegramServerError,
)

from app.config import settings

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 4
MAX_RETRY_AFTER = 60  # seconds; never wait longer than this for a flood limit


class RetryMiddleware(BaseRequestMiddleware):
    def __init__(self, attempts: int = MAX_ATTEMPTS, base_delay: float = 1.0):
        self.attempts = attempts
        self.base_delay = base_delay

    async def __call__(self, make_request, bot, method):
        for attempt in range(1, self.attempts + 1):
            try:
                return await make_request(bot, method)
            except TelegramRetryAfter as error:
                if attempt == self.attempts or error.retry_after > MAX_RETRY_AFTER:
                    raise
                logger.warning("Telegram flood limit, waiting %ss (%s)", error.retry_after, type(method).__name__)
                await asyncio.sleep(error.retry_after)
            except (TelegramNetworkError, TelegramServerError) as error:
                if attempt == self.attempts:
                    raise
                delay = self.base_delay * 2 ** (attempt - 1)
                logger.warning("Telegram error %s, retry %s in %ss", error, attempt, delay)
                await asyncio.sleep(delay)
        raise RuntimeError("unreachable")


def make_bot(token: str | None = None) -> Bot:
    bot = Bot(token=token or settings.bot_token)
    bot.session.middleware(RetryMiddleware())
    return bot


_bot: Bot | None = None


def get_bot() -> Bot | None:
    """The shared Bot for sending from the dashboard. None when BOT_TOKEN is not set."""
    global _bot
    if _bot is None and settings.bot_token:
        _bot = make_bot()
    return _bot


async def send_text(chat_id: int, text: str) -> tuple[bool, str]:
    """Send a message. Returns (delivered, error text)."""
    bot = get_bot()
    if bot is None:
        return False, "BOT_TOKEN is not set"
    try:
        await bot.send_message(chat_id, text)
        return True, ""
    except TelegramForbiddenError:
        return False, "user blocked the bot"
    except TelegramAPIError as error:
        logger.warning("send to %s failed: %s", chat_id, error)
        return False, str(error)
