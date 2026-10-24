"""Build the bot and dispatcher. Used by Long Polling (app.bot.main) and Webhook mode (app.web.webhook)."""
import logging

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.types import BotCommand

from app.bot.handlers import router
from app.bot.middlewares import DbSessionMiddleware, ProtectionMiddleware
from app.db import SessionLocal, init_db
from app.seed import seed_defaults
from app.services.telegram import make_bot

COMMANDS = [
    BotCommand(command="start", description="Start the bot"),
    BotCommand(command="help", description="Show help"),
    BotCommand(command="menu", description="Show the main menu"),
    BotCommand(command="cancel", description="Stop the current form"),
]


def build_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.update.outer_middleware(DbSessionMiddleware())
    dispatcher.message.middleware(ProtectionMiddleware())  # rate limit, spam, moderation
    dispatcher.include_router(router)
    return dispatcher


async def prepare_bot() -> Bot:
    """Database ready, token checked with Telegram (Bot Authentication), command list set."""
    await init_db()
    async with SessionLocal() as session:
        await seed_defaults(session)
    bot = make_bot()  # with retry for Telegram API errors
    try:
        me = await bot.get_me()
    except TelegramUnauthorizedError:
        await bot.session.close()
        raise SystemExit("Invalid BOT_TOKEN. Check the token from @BotFather.")
    logging.info("Authenticated as @%s", me.username)
    await bot.set_my_commands(COMMANDS)
    return bot
