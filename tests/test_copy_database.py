"""Copying all data to another database (used for the SQLite -> PostgreSQL switch)."""
import asyncio
import sqlite3

import pytest

from app.db import SessionLocal, init_db
from app.seed import seed_defaults
from scripts.copy_database import copy


def test_copy_to_an_empty_database(tmp_path):
    async def seed():
        await init_db()
        async with SessionLocal() as session:
            await seed_defaults(session)
    asyncio.run(seed())
    from app.config import settings

    target = tmp_path / "copy.db"
    counts = asyncio.run(copy(settings.database_url, f"sqlite+aiosqlite:///{target}"))
    assert counts["faqs"] >= 3 and counts["intents"] >= 3
    with sqlite3.connect(target) as con:
        assert con.execute("select count(*) from faqs").fetchone()[0] == counts["faqs"]

    with pytest.raises(SystemExit):  # the target is not empty any more
        asyncio.run(copy(settings.database_url, f"sqlite+aiosqlite:///{target}"))
