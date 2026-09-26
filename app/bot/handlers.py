"""Telegram handlers: commands, menu buttons, callback queries, messages."""
import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot import keyboards as kb
from app.i18n import button_key, t
from app.models import FAQ, Bot, Feedback, Source, UserStatus
from app.models import Command as BotCommand
from app.services import users as svc
from app.services.router import route_message

logger = logging.getLogger(__name__)
router = Router()


# ---- helpers -----------------------------------------------------------------
async def _load(session: AsyncSession, tg_user):
    """Register/update the user and return (user, open conversation, is_new)."""
    user, created = await svc.get_or_create_user(
        session, tg_user.id, tg_user.username, tg_user.full_name
    )
    conversation = await svc.get_open_conversation(session, user)
    return user, conversation, created


async def _allowed(session: AsyncSession, user, target: Message) -> bool:
    """Blocked / suspended users and Maintenance Mode."""
    if user.status in (UserStatus.BLOCKED, UserStatus.SUSPENDED):
        await target.answer(t(user.language, "blocked"))
        return False
    bot = (await session.execute(select(Bot))).scalars().first()
    if bot and (bot.maintenance_mode or bot.working_status != "enabled"):
        await target.answer(t(user.language, "maintenance"))
        return False
    return True


async def _send(session, target: Message, user, conversation, text: str, source: str, markup=None):
    """Save the outgoing message, then send it. `markup` may be a function(message_id)."""
    db_message = await svc.save_message(session, conversation, user, "outgoing", text, source=source)
    if callable(markup):
        markup = markup(db_message.id)
    await target.answer(text, reply_markup=markup)
    return db_message


async def _show_main_menu(session, target: Message, user, conversation, text_key: str = "menu_title"):
    await _send(session, target, user, conversation, t(user.language, text_key), Source.COMMAND,
                kb.main_menu(user.language))


async def _show_faq_list(session, target: Message, user, conversation):
    result = await session.execute(select(FAQ).where(FAQ.status == "Active").order_by(FAQ.priority.desc()))
    faqs = [f for f in result.scalars() if f.language == user.language][:10]
    if not faqs:
        await _send(session, target, user, conversation, t(user.language, "faq_empty"), Source.COMMAND)
        return
    await _send(session, target, user, conversation, t(user.language, "faq_title"), Source.COMMAND,
                kb.faq_keyboard(faqs))


async def _human_support(session, target: Message, user, conversation):
    await svc.request_human_support(session, conversation)
    await _send(session, target, user, conversation, t(user.language, "handoff_created"), Source.COMMAND)


# ---- commands ----------------------------------------------------------------
@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    user, conversation, created = await _load(session, message.from_user)
    if not await _allowed(session, user, message):
        return
    if message.text is not None:
        await svc.save_message(session, conversation, user, "incoming", message.text)
    if created:  # new user: choose language first
        await _send(session, message, user, conversation, t(user.language, "choose_language"),
                    Source.COMMAND, kb.language_keyboard())
    else:
        await _show_main_menu(session, message, user, conversation, "welcome")


@router.message(Command("help"))
async def cmd_help(message: Message, session: AsyncSession):
    user, conversation, _ = await _load(session, message.from_user)
    if not await _allowed(session, user, message):
        return
    if not message.text:
        return
    await svc.save_message(session, conversation, user, "incoming", message.text)
    await _send(session, message, user, conversation, t(user.language, "help"), Source.COMMAND,
                kb.main_menu(user.language))


@router.message(Command("menu"))
async def cmd_menu(message: Message, session: AsyncSession):
    user, conversation, _ = await _load(session, message.from_user)
    if not await _allowed(session, user, message):
        return
    if not message.text:
        return
    await svc.save_message(session, conversation, user, "incoming", message.text)
    await _show_main_menu(session, message, user, conversation)


@router.message(F.text.startswith("/"))
async def custom_command(message: Message, session: AsyncSession):
    """Custom commands created by admins (stored in the commands table)."""
    user, conversation, _ = await _load(session, message.from_user)
    if not await _allowed(session, user, message):
        return
    if not message.text:
        return
    await svc.save_message(session, conversation, user, "incoming", message.text)
    name = message.text[1:].split()[0].split("@")[0].lower()
    result = await session.execute(
        select(BotCommand).where(BotCommand.name == name, BotCommand.status == "Active")
    )
    command = result.scalar_one_or_none()
    if command:
        await _send(session, message, user, conversation, command.response, Source.COMMAND)
    else:
        await _send(session, message, user, conversation, t(user.language, "fallback"), Source.FALLBACK,
                    kb.fallback_keyboard(user.language))


# ---- Main Menu buttons (Reply Keyboard) ---------------------------------------
@router.message(F.text.func(lambda text: button_key(text) is not None))
async def on_menu_button(message: Message, session: AsyncSession):
    user, conversation, _ = await _load(session, message.from_user)
    if not await _allowed(session, user, message):
        return
    if not message.text:
        return
    await svc.save_message(session, conversation, user, "incoming", message.text)
    key = button_key(message.text)
    lang = user.language
    if key == "btn_ask":
        await _send(session, message, user, conversation, t(lang, "ask_prompt"), Source.COMMAND)
    elif key == "btn_faq":
        await _show_faq_list(session, message, user, conversation)
    elif key == "btn_contact":
        bot = (await session.execute(select(Bot))).scalars().first()
        contact = bot.support_contact if bot else "-"
        await _send(session, message, user, conversation, t(lang, "contact", contact=contact), Source.COMMAND)
    elif key == "btn_support":
        await _human_support(session, message, user, conversation)
    elif key == "btn_language":
        await _send(session, message, user, conversation, t(lang, "choose_language"), Source.COMMAND,
                    kb.language_keyboard())
    elif key == "btn_feedback":
        await _send(session, message, user, conversation, t(lang, "feedback_prompt"), Source.COMMAND,
                    kb.rating_keyboard())


# ---- callback queries (Inline Keyboard) ---------------------------------------
@router.callback_query(F.data.startswith("lang:"))
async def on_language(callback: CallbackQuery, session: AsyncSession):
    if not isinstance(callback.message, Message):
        await callback.answer()
        return
    user, conversation, _ = await _load(session, callback.from_user)
    if not callback.data:
        return
    user.language = callback.data.split(":")[1]
    await session.commit()
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await _show_main_menu(session, callback.message, user, conversation, "welcome")


@router.callback_query(F.data.startswith("faq:"))
async def on_faq(callback: CallbackQuery, session: AsyncSession):
    if not isinstance(callback.message, Message):
        await callback.answer()
        return
    user, conversation, _ = await _load(session, callback.from_user)
    if not callback.data:
        return
    faq = await session.get(FAQ, int(callback.data.split(":")[1]))
    await callback.answer()
    if faq:
        await _send(session, callback.message, user, conversation, faq.answer, Source.FAQ,
                    kb.feedback_keyboard)


@router.callback_query(F.data.startswith("fb:"))
async def on_feedback(callback: CallbackQuery, session: AsyncSession):
    if not isinstance(callback.message, Message):
        await callback.answer()
        return
    if not callback.data:
        return
    _, rating, message_id = callback.data.split(":")
    user, conversation, _ = await _load(session, callback.from_user)
    session.add(Feedback(
        user_id=user.id, conversation_id=conversation.id,
        message_id=int(message_id) if message_id != "0" else None, rating=int(rating),
    ))
    await session.commit()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer(t(user.language, "feedback_thanks"))


@router.callback_query(F.data.startswith("menu:"))
async def on_menu_callback(callback: CallbackQuery, session: AsyncSession):
    if not isinstance(callback.message, Message):
        await callback.answer()
        return
    user, conversation, _ = await _load(session, callback.from_user)
    if not callback.data:
        return
    action = callback.data.split(":")[1]
    await callback.answer()
    if action == "ask":
        await _send(session, callback.message, user, conversation, t(user.language, "ask_prompt"), Source.COMMAND)
    elif action == "main":
        await _show_main_menu(session, callback.message, user, conversation)
    elif action == "human":
        await _human_support(session, callback.message, user, conversation)


# ---- normal messages ----------------------------------------------------------
@router.message(F.text)
async def on_text(message: Message, session: AsyncSession):
    """Free-text question -> Response Routing Logic."""
    user, conversation, _ = await _load(session, message.from_user)
    if not await _allowed(session, user, message):
        return
    if not message.text:
        return
    await svc.save_message(session, conversation, user, "incoming", message.text)
    reply = await route_message(session, user, message.text)
    markup = kb.fallback_keyboard(user.language) if reply.fallback else kb.feedback_keyboard
    await _send(session, message, user, conversation, reply.text, reply.source, markup)


@router.message(F.photo | F.document | F.voice | F.location)
async def on_media(message: Message, session: AsyncSession):
    """Image, document, voice (prototype) and location messages are stored."""
    user, conversation, _ = await _load(session, message.from_user)
    if not await _allowed(session, user, message):
        return
    if message.photo:
        kind, content = "image", message.photo[-1].file_id
    elif message.document:
        kind, content = "document", message.document.file_id
    elif message.voice:
        kind, content = "voice", message.voice.file_id
    elif message.location:
        kind, content = "location", f"{message.location.latitude},{message.location.longitude}"
    else:
        kind, content = "other", ""
    await svc.save_message(session, conversation, user, "incoming", content, message_type=kind)
    await _send(session, message, user, conversation, t(user.language, "received_file", kind=kind), Source.COMMAND)


@router.message()
async def on_unsupported(message: Message, session: AsyncSession):
    user, conversation, _ = await _load(session, message.from_user)
    await svc.save_message(session, conversation, user, "incoming", "", message_type="unsupported")
    await _send(session, message, user, conversation, t(user.language, "unsupported"), Source.FALLBACK)
