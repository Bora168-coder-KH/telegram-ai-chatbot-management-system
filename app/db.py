"""Async database engine and session factory (SQLAlchemy 2.0)."""
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.config import settings

# SQLite: open a fresh connection each time (simple and safe for a prototype).
_options = {"poolclass": NullPool} if settings.database_url.startswith("sqlite") else {}
engine = create_async_engine(settings.database_url, echo=False, **_options)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    """Create all tables. Good enough for the prototype.

    TODO (learning task): replace with Alembic migrations.
    """
    from app import models  # noqa: F401  (registers the models on Base)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
