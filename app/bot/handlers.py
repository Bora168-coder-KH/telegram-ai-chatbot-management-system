"""Telegram handlers: commands, menu buttons, callback queries, messages."""
import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot import keyboards as kb
from app.i18n import button_key, category_label, t
from app.models import FAQ, FAQ_CATEGORIES, Bot, Feedback, Source, UserStatus
from app.models import Command as BotCommand
from app.services import forms
from app.services import users as svc
from app.services.handoff import request_human_support
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


async def _active_faqs(session: AsyncSession, language: str) -> list[FAQ]:
    result = await session.execute(select(FAQ).where(FAQ.status == "Active").order_by(FAQ.priority.desc(), FAQ.id))
    return [f for f in result.scalars() if f.language == language]


async def _faq_categories(session: AsyncSession, language: str) -> list[str]:
    """Categories that have at least one active FAQ, in dashboard order (unknown ones last)."""
    found = {f.category for f in await _active_faqs(session, language)}
    known = [c for c in FAQ_CATEGORIES if c in found]
    return known + sorted(found - set(FAQ_CATEGORIES))


async def _show_faq_categories(session, target: Message, user, conversation):
    categories = await _faq_categories(session, user.language)
    if not categories:
        await _send(session, target, user, conversation, t(user.language, "faq_empty"), Source.COMMAND)
        return
    await _send(session, target, user, conversation, t(user.language, "faq_choose_category"), Source.COMMAND,
                kb.faq_category_keyboard(categories, user.language))


async def _human_support(session, target: Message, user, conversation):
    await request_human_support(session, conversation)
    await _send(session, target, user, conversation, t(user.language, "handoff_created"), Source.COMMAND)


async def _send_form_reply(session, target: Message, user, conversation, reply: forms.FormReply):
    markup = kb.confirm_keyboard(user.language) if reply.confirm else None
    if reply.finished:
        markup = kb.main_menu(user.language)
    await _send(session, target, user, conversation, reply.text, Source.COMMAND, markup)


async def _start_form(session, target: Message, user, conversation):
    reply = await forms.start_form(session, conversation, user.language)
    await _send_form_reply(session, target, user, conversation, reply)


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


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, session: AsyncSession):
    user, conversation, _ = await _load(session, message.from_user)
    if not await _allowed(session, user, message):
        return
    if not message.text:
        return
    await svc.save_message(session, conversation, user, "incoming", message.text)
    reply = await forms.cancel_form(session, conversation, user.language)
    await _send_form_reply(session, message, user, conversation, reply)


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
        await _show_faq_categories(session, message, user, conversation)
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
    elif key == "btn_form":
        await _start_form(session, message, user, conversation)


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


@router.callback_query(F.data.startswith("faqcat:"))
async def on_faq_category(callback: CallbackQuery, session: AsyncSession):
    """Category chosen: replace the category list with that category's questions."""
    if not isinstance(callback.message, Message):
        await callback.answer()
        return
    user, _, _ = await _load(session, callback.from_user)
    if not callback.data:
        return
    category = callback.data.split(":", 1)[1]
    faqs = [f for f in await _active_faqs(session, user.language) if f.category == category]
    await callback.answer()
    if not faqs:
        await callback.message.edit_text(t(user.language, "faq_empty"))
        return
    title = t(user.language, "faq_category_title", category=category_label(user.language, category))
    await callback.message.edit_text(title,
                                     reply_markup=kb.faq_keyboard(faqs, user.language))


@router.callback_query(F.data == "faqback")
async def on_faq_back(callback: CallbackQuery, session: AsyncSession):
    """Back button: show the category list again in the same message."""
    if not isinstance(callback.message, Message):
        await callback.answer()
        return
    user, _, _ = await _load(session, callback.from_user)
    categories = await _faq_categories(session, user.language)
    await callback.answer()
    await callback.message.edit_text(t(user.language, "faq_choose_category"),
                                     reply_markup=kb.faq_category_keyboard(categories, user.language))


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


@router.callback_query(F.data.startswith("form:"))
async def on_form_confirm(callback: CallbackQuery, session: AsyncSession):
    """Yes / No under the form summary."""
    if not isinstance(callback.message, Message):
        await callback.answer()
        return
    user, conversation, _ = await _load(session, callback.from_user)
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    if conversation.session_step != "confirm":
        return  # old button: the form was already sent or cancelled
    if callback.data == "form:yes":
        reply = await forms.submit_form(session, conversation, user, user.language)
    else:
        reply = await forms.cancel_form(session, conversation, user.language)
    await _send_form_reply(session, callback.message, user, conversation, reply)


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
    if forms.in_form(conversation):  # the user is answering a form step
        form_reply = await forms.handle_form_input(session, conversation, user, message.text)
        await _send_form_reply(session, message, user, conversation, form_reply)
        return
    reply = await route_message(session, user, message.text)
    if reply.intent:
        conversation.intent = reply.intent
        if reply.entities:
            conversation.context = {**(conversation.context or {}), "entities": reply.entities}
        await session.commit()
    if reply.start_form:
        await _start_form(session, message, user, conversation)
        return
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
