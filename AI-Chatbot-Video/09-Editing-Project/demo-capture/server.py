"""Run the real dashboard. Telegram is replaced by a recorder (no bot token here)."""
import json, sys
from pathlib import Path
from types import SimpleNamespace
import uvicorn
from app.services import broadcast, telegram
from app.web.main import app

OUTBOX = Path(__file__).with_name("outbox.json")
OUTBOX.write_text("[]")

class FakeBot:
    async def send_message(self, chat_id, text, **kw):
        data = json.loads(OUTBOX.read_text()); data.append({"chat_id": chat_id, "text": text})
        OUTBOX.write_text(json.dumps(data, ensure_ascii=False, indent=1))
        return SimpleNamespace(message_id=len(data))
    async def __getattr__(self, name):  # pragma: no cover
        raise AttributeError(name)

fake = FakeBot()
telegram.get_bot = lambda: fake
broadcast.SEND_DELAY = 0
uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning")
