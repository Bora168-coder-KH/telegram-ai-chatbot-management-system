"""Test setup: use a temporary SQLite database, never the real one."""
import os
import tempfile

_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_tmp}/test.db"
os.environ["BOT_TOKEN"] = ""
os.environ["AI_API_KEY"] = ""
