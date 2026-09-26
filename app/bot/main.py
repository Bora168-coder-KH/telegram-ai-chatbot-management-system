"""Run the Telegram bot (Long Polling):  python -m app.bot.main"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.types import BotCommand

from app.bot.handlers import router
from app.bot.middlewares import DbSessionMiddleware
from app.config import settings
from app.db import SessionLocal, init_db
from app.seed import seed_defaults


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if not settings.bot_token:
        raise SystemExit("BOT_TOKEN is missing. Copy .env.example to .env and set your token.")

    await init_db()
    async with SessionLocal() as session:
        await seed_defaults(session)  # sample data for the prototype

    bot = Bot(token=settings.bot_token)
    try:
        me = await bot.get_me()  # Bot Authentication: Telegram verifies the token
    except TelegramUnauthorizedError:
        raise SystemExit("Invalid BOT_TOKEN. Check the token from @BotFather.")
    logging.info("Authenticated as @%s", me.username)

    await bot.set_my_commands([
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="help", description="Show help"),
        BotCommand(command="menu", description="Show the main menu"),
    ])

    dispatcher = Dispatcher()
    dispatcher.update.outer_middleware(DbSessionMiddleware())
    dispatcher.include_router(router)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
