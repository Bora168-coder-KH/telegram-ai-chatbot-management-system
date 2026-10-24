"""Backup and recovery script (SQLite)."""
import sqlite3

import pytest

from scripts import backup


def _db(path, value: str):
    with sqlite3.connect(path) as con:
        con.execute("create table if not exists t (v text)")
        con.execute("delete from t")
        con.execute("insert into t values (?)", (value,))


def _value(path) -> str:
    with sqlite3.connect(path) as con:
        return con.execute("select v from t").fetchone()[0]


def test_backup_and_restore(tmp_path):
    db = tmp_path / "live.db"
    url = f"sqlite+aiosqlite:///{db}"
    folder = tmp_path / "backups"
    _db(db, "before")
    saved = backup.backup(url, folder)
    assert _value(saved) == "before"

    _db(db, "after a mistake")
    safety = backup.restore(saved, url, folder)
    assert _value(db) == "before"
    assert _value(safety) == "after a mistake"  # the current data was kept before restoring


def test_keeps_only_the_newest(tmp_path):
    db = tmp_path / "live.db"
    _db(db, "x")
    for _ in range(4):
        backup.backup(f"sqlite+aiosqlite:///{db}", tmp_path / "b", keep=2)
    assert len(list((tmp_path / "b").glob("chatbot-*.db"))) == 2


def test_damaged_backup_is_refused(tmp_path):
    bad = tmp_path / "chatbot-bad.db"
    bad.write_bytes(b"not a database")
    with pytest.raises((SystemExit, sqlite3.DatabaseError)):
        backup.restore(bad, f"sqlite+aiosqlite:///{tmp_path / 'live.db'}", tmp_path / "b")
