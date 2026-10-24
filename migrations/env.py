"""Alembic environment: uses the app's async engine and models."""
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app import models  # noqa: F401  (registers the models on Base)
from app.config import settings
from app.db import Base

config = context.config
if config.config_file_name is not None and config.attributes.get("configure_logging", True):
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _configure(connection=None) -> None:
    # render_as_batch: SQLite cannot ALTER most things, batch mode copies the table instead.
    options = dict(target_metadata=target_metadata, render_as_batch=True, compare_type=True)
    if connection is None:
        context.configure(url=settings.database_url, literal_binds=True, **options)
    else:
        context.configure(connection=connection, **options)


def _run_sync(connection) -> None:
    _configure(connection)
    with context.begin_transaction():
        context.run_migrations()


async def _run_async() -> None:
    engine = create_async_engine(settings.database_url)
    async with engine.connect() as connection:
        await connection.run_sync(_run_sync)
    await engine.dispose()


if context.is_offline_mode():
    _configure()
    with context.begin_transaction():
        context.run_migrations()
else:
    connection = config.attributes.get("connection")
    if connection is not None:  # called from app.db.init_db with an open connection
        _run_sync(connection)
    else:
        asyncio.run(_run_async())
