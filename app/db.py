"""Async database engine and session factory (SQLAlchemy 2.0)."""
from pathlib import Path

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.config import settings

ROOT = Path(__file__).resolve().parent.parent
BASELINE_REVISION = "0001"  # the schema the old create_all() used to build

# SQLite: open a fresh connection each time (simple and safe for a prototype).
_options = {"poolclass": NullPool} if settings.database_url.startswith("sqlite") else {}
engine = create_async_engine(settings.database_url, echo=False, **_options)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def _migrate(connection) -> None:
    from alembic import command
    from alembic.config import Config

    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "migrations"))
    config.attributes["connection"] = connection
    config.attributes["configure_logging"] = False
    tables = inspect(connection).get_table_names()
    if tables and "alembic_version" not in tables:
        # A database made by create_all() before migrations existed: mark it as the baseline.
        command.stamp(config, BASELINE_REVISION)
    command.upgrade(config, "head")


async def init_db() -> None:
    """Bring the database schema up to date with the Alembic migrations (migrations/)."""
    async with engine.begin() as conn:
        await conn.run_sync(_migrate)
