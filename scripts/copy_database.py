"""Copy every row from one database to another, e.g. from SQLite to PostgreSQL.

    python -m scripts.copy_database sqlite+aiosqlite:///./chatbot.db \
        postgresql+asyncpg://chatbot:chatbot@localhost:5432/chatbot

The target is migrated to the latest schema first (Alembic) and must be empty.
Tables are copied parent-first so foreign keys are satisfied; on PostgreSQL the
id sequences are moved past the copied ids so new rows do not collide.
"""
import argparse
import asyncio

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import create_async_engine

from app import models  # noqa: F401  (registers the models on Base)
from app.db import Base, _migrate


async def copy(source_url: str, target_url: str) -> dict[str, int]:
    source = create_async_engine(source_url)
    target = create_async_engine(target_url)
    counts: dict[str, int] = {}
    try:
        async with source.connect() as src:
            await src.run_sync(_migrate)  # make sure the source has the latest columns too
            await src.commit()
        async with target.begin() as dst:
            await dst.run_sync(_migrate)
        async with source.connect() as src, target.begin() as dst:
            for table in Base.metadata.sorted_tables:
                if (await dst.execute(select(func.count()).select_from(table))).scalar_one():
                    raise SystemExit(f"Target table {table.name} is not empty; use an empty database.")
            for table in Base.metadata.sorted_tables:
                rows = [dict(row._mapping) for row in await src.execute(select(table))]
                if rows:
                    await dst.execute(table.insert(), rows)
                counts[table.name] = len(rows)
                if dst.dialect.name == "postgresql" and rows and "id" in table.c:
                    await dst.execute(text(
                        f"select setval(pg_get_serial_sequence('{table.name}', 'id'), "
                        f"(select max(id) from {table.name}))"
                    ))
    finally:
        await source.dispose()
        await target.dispose()
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source")
    parser.add_argument("target")
    args = parser.parse_args()
    for name, count in asyncio.run(copy(args.source, args.target)).items():
        print(f"{name:20} {count}")


if __name__ == "__main__":
    main()
