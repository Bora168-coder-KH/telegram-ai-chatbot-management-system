"""Play the students' Telegram messages through the real bot handlers; save the bot's real replies."""
import asyncio, json, sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock
from sqlalchemy import select, func
from app.bot import handlers
from app.db import SessionLocal
from app.mock_data import seed_mock_faqs
from app.models import FAQ, Message, TelegramUser

handlers.Message = SimpleNamespace
OUT = Path(__file__).with_name("transcript.json")
LOG = json.loads(OUT.read_text()) if OUT.exists() else {}

def markup_buttons(markup):
    if markup is None: return []
    if hasattr(markup, "inline_keyboard"):
        return [[b.text for b in row] for row in markup.inline_keyboard]
    if hasattr(markup, "keyboard"):
        return [[b.text for b in row] for row in markup.keyboard]
    return []

def replies(mock):
    out = []
    for call in mock.call_args_list:
        m = call.kwargs.get("reply_markup")
        if callable(m): m = None
        out.append({"text": call.args[0], "buttons": markup_buttons(m),
                    "kind": "reply" if m is not None and hasattr(m, "keyboard") else "inline"})
    return out

async def last_out_id(session, tg_id):
    uid = (await session.execute(select(TelegramUser.id).where(TelegramUser.telegram_user_id == tg_id))).scalar_one()
    return (await session.execute(select(func.max(Message.id)).where(Message.user_id == uid, Message.direction == "outgoing"))).scalar_one()

async def say(user, text, menu=False):
    msg = SimpleNamespace(text=text, from_user=user, answer=AsyncMock())
    async with SessionLocal() as s:
        if text.startswith("/start"): await handlers.cmd_start(msg, s)
        elif menu: await handlers.on_menu_button(msg, s)
        else: await handlers.on_text(msg, s)
    return {"user": text, "bot": replies(msg.answer)}

async def tap(user, data, label):
    message = SimpleNamespace(answer=AsyncMock(), edit_text=AsyncMock(), edit_reply_markup=AsyncMock())
    cb = SimpleNamespace(data=data, from_user=user, message=message, answer=AsyncMock())
    h = {"lang": handlers.on_language, "fb": handlers.on_feedback, "menu": handlers.on_menu_callback}[data.split(":")[0]]
    async with SessionLocal() as s:
        await h(cb, s)
    toast = [c.args[0] for c in cb.answer.call_args_list if c.args]
    return {"tap": label, "bot": replies(message.answer), "toast": toast}

SOKHA = SimpleNamespace(id=8100001, username="sok_sokha", full_name="Sok Sokha")
STUDENT_B = SimpleNamespace(id=8100002, username="student_b", full_name="Chan Vibol")
OTHERS = [
    (SimpleNamespace(id=8100010 + i, username=f"student{i}", full_name=n), q)
    for i, (n, q) in enumerate([
        ("Keo Malis", "What documents do I need to register?"),
        ("Lim Dara", "When is the registration deadline?"),
        ("Heng Sophea", "Is there a registration fee?"),
        ("Chea Rithy", "Can I register online?"),
        ("Ouk Sreyneang", "តើខ្ញុំត្រូវការឯកសារអ្វីខ្លះដើម្បីចុះឈ្មោះ?"),
        ("Pich Vanna", "Can I pay in installments?"),
    ])]

async def phase1():
    async with SessionLocal() as s:
        if not (await s.execute(select(FAQ))).scalars().first() or True:
            await seed_mock_faqs(s)
    for user, q in OTHERS:
        await say(user, "/start"); await tap(user, "lang:" + ("km" if q[0] > "ᜀ" else "en"), "lang")
        await say(user, q)
    steps = []
    steps.append(await say(SOKHA, "/start"))
    steps.append(await tap(SOKHA, "lang:km", "ខ្មែរ"))
    steps.append(await say(SOKHA, "តើចុះឈ្មោះចូលរៀន ត្រូវការឯកសារអ្វីខ្លះ?"))
    async with SessionLocal() as s: mid = await last_out_id(s, SOKHA.id)
    steps.append(await tap(SOKHA, f"fb:5:{mid}", "👍"))
    steps.append(await tap(SOKHA, "lang:en", "English"))
    steps.append(await say(SOKHA, "What are the required documents for registration?"))
    steps.append(await say(SOKHA, "I want to book an appointment on 2026-12-15"))
    steps.append(await say(SOKHA, "Is there a bus to campus?"))
    steps.append(await tap(SOKHA, "menu:human", "Human Support"))
    LOG["sokha"] = steps

async def phase2():
    steps = [await say(STUDENT_B, "/start"), await tap(STUDENT_B, "lang:en", "English"),
             await say(STUDENT_B, "Is there a shuttle bus to the campus?")]
    LOG["student_b"] = steps

asyncio.run({"1": phase1, "2": phase2}[sys.argv[1]]())
OUT.write_text(json.dumps(LOG, ensure_ascii=False, indent=1))
print(json.dumps(LOG, ensure_ascii=False, indent=1)[:6000])
