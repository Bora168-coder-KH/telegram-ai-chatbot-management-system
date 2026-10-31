"""Backup and recovery for the chatbot database (prototype).

    python -m scripts.backup backup            make a backup in backups/ (keeps the newest 10)
    python -m scripts.backup list              show backups
    python -m scripts.backup restore FILE      put a backup back (the current database is backed up first)

SQLite uses the sqlite3 online backup API, so it is safe while the bot is running.
PostgreSQL uses pg_dump / pg_restore (they must be installed).
Stop the bot and the dashboard before a restore.
"""
import argparse
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from app.config import settings

BACKUP_DIR = Path("backups")
KEEP = 10


def _sqlite_path(url: str) -> Path | None:
    if not url.startswith("sqlite"):
        return None
    return Path(url.split("///", 1)[1])


def _pg_env(url: str) -> tuple[list[str], dict]:
    parsed = urlparse(url.replace("+asyncpg", ""))
    env = {**os.environ, "PGPASSWORD": parsed.password or ""}
    args = ["-h", parsed.hostname or "localhost", "-p", str(parsed.port or 5432), "-U", parsed.username or "postgres",
            "-d", parsed.path.lstrip("/")]
    return args, env


def backup(url: str = settings.database_url, folder: Path = BACKUP_DIR, keep: int = KEEP) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    db_file = _sqlite_path(url)
    if db_file is not None:
        if not db_file.exists():
            raise SystemExit(f"Database file {db_file} does not exist")
        target = folder / f"chatbot-{stamp}.db"
        with sqlite3.connect(db_file) as source, sqlite3.connect(target) as dest:
            source.backup(dest)
        pattern = "chatbot-*.db"
    else:
        args, env = _pg_env(url)
        target = folder / f"chatbot-{stamp}.dump"
        subprocess.run(["pg_dump", "-Fc", "-f", str(target), *args], env=env, check=True)
        pattern = "chatbot-*.dump"
    for old in sorted(folder.glob(pattern))[:-keep]:
        old.unlink()
    return target


def check(path: Path) -> None:
    """A SQLite backup must open and pass an integrity check."""
    if path.suffix == ".db":
        with sqlite3.connect(path) as con:
            result = con.execute("pragma integrity_check").fetchone()[0]
        if result != "ok":
            raise SystemExit(f"{path} is damaged: {result}")


def restore(path: Path, url: str = settings.database_url, folder: Path = BACKUP_DIR) -> Path | None:
    if not path.exists():
        raise SystemExit(f"{path} does not exist")
    check(path)
    db_file = _sqlite_path(url)
    safety = backup(url, folder) if db_file is None or db_file.exists() else None
    if db_file is not None:
        shutil.copyfile(path, db_file)
    else:
        args, env = _pg_env(url)
        subprocess.run(["pg_restore", "--clean", "--if-exists", "--no-owner", *args, str(path)], env=env, check=True)
    return safety


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("backup")
    sub.add_parser("list")
    restore_cmd = sub.add_parser("restore")
    restore_cmd.add_argument("file", type=Path)
    args = parser.parse_args(argv)

    if args.command == "backup":
        print(f"Backup written to {backup()}")
    elif args.command == "list":
        files = sorted(BACKUP_DIR.glob("chatbot-*"))
        for f in files:
            print(f"{f}  {f.stat().st_size // 1024} KB")
        if not files:
            print("No backups yet.")
    elif args.command == "restore":
        safety = restore(args.file)
        if safety:
            print(f"The previous database was saved to {safety}")
        print(f"Restored {args.file}")


if __name__ == "__main__":
    main(sys.argv[1:])
