"""Run the Telegram bot with Long Polling:  python -m app.bot.main

For Webhook mode set BOT_MODE=webhook and run only the dashboard (see app/web/webhook.py).
"""
import asyncio
import logging

from app.bot.runtime import build_dispatcher, prepare_bot
from app.config import settings
from app.services.scheduler import build_scheduler


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if not settings.bot_token:
        raise SystemExit("BOT_TOKEN is missing. Copy .env.example to .env and set your token.")
    if settings.bot_mode == "webhook":
        raise SystemExit("BOT_MODE=webhook: the dashboard receives updates, do not run the polling bot.")

    bot = await prepare_bot()
    await bot.delete_webhook()  # polling does not work while a webhook is set
    scheduler = build_scheduler()  # scheduled broadcasts and reminders
    scheduler.start()
    try:
        await build_dispatcher().start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
