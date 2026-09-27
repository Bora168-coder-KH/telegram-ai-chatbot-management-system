"""Gives every handler its own database session (`session` argument)."""
from aiogram import BaseMiddleware

from app.db import SessionLocal


class DbSessionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        async with SessionLocal() as session:
            data["session"] = session
            return await handler(event, data)
