"""Alembic migrations: a fresh database and an old create_all() database both reach head."""
import asyncio
import sqlite3
import tempfile

from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine

from app import db


def _run(path: str, step) -> None:
    async def run():
        engine = create_async_engine(f"sqlite+aiosqlite:///{path}")
        async with engine.begin() as conn:
            await conn.run_sync(step)
        await engine.dispose()
    asyncio.run(run())


def _upgrade_to_baseline(connection) -> None:
    config = Config(str(db.ROOT / "alembic.ini"))
    config.attributes.update(connection=connection, configure_logging=False)
    command.upgrade(config, db.BASELINE_REVISION)


def test_fresh_database_reaches_head():
    path = tempfile.mktemp(suffix=".db")
    _run(path, db._migrate)
    con = sqlite3.connect(path)
    assert con.execute("select version_num from alembic_version").fetchone() == ("0002",)
    columns = [row[1] for row in con.execute("pragma table_info(telegram_users)")]
    assert "phone" in columns and "email" in columns


def test_old_create_all_database_is_stamped_then_upgraded():
    # An old database: baseline tables with data, but no alembic_version table.
    path = tempfile.mktemp(suffix=".db")
    _run(path, _upgrade_to_baseline)
    con = sqlite3.connect(path)
    con.execute("drop table alembic_version")
    con.execute("insert into faqs (question, answer, category, keywords, language, priority, status)"
                " values ('Old question?', 'Old answer', 'General', '', 'en', 0, 'Active')")
    con.commit()

    _run(path, db._migrate)
    assert con.execute("select version_num from alembic_version").fetchone() == ("0002",)
    assert con.execute("select question from faqs").fetchone() == ("Old question?",)
