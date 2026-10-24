"""Form conversation: Name -> Phone -> Email -> Request -> Confirmation.

The current step is kept in `Conversation.session_step` and the answers so far in
`Conversation.context["form"]`, so the form survives a bot restart.
No Telegram code here: the bot layer shows the returned text (and Yes/No buttons
when `confirm` is True).
"""
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.i18n import t
from app.models import Conversation, TelegramUser
from app.services import logs, validators
from app.services.text import normalize

STEPS = ["name", "phone", "email", "request", "confirm"]
FORM_INTENT = "contact_request"  # this intent starts the form
CANCEL_WORDS = {"cancel", "stop", "បោះបង់"}
YES_WORDS = {"yes", "y", "ok", "confirm", "បាទ", "ចាស", "យល់ព្រម"}
NO_WORDS = {"no", "n", "ទេ"}


@dataclass
class FormReply:
    text: str
    confirm: bool = False  # show Yes / No buttons
    finished: bool = False  # submitted or cancelled


def in_form(conversation: Conversation) -> bool:
    return conversation.session_step in STEPS


def _set(conversation: Conversation, step: str | None, form: dict | None) -> None:
    # Reassign the JSON column: changing the dict in place would not be saved.
    context = {k: v for k, v in (conversation.context or {}).items() if k != "form"}
    if form is not None:
        context["form"] = form
    conversation.context = context
    conversation.session_step = step


def _valid_request(text: str) -> str | None:
    text = text.strip()
    return text if 5 <= len(text) <= 1000 else None


VALIDATORS = {
    "name": validators.valid_name,
    "phone": validators.valid_phone,
    "email": validators.valid_email,
    "request": _valid_request,
}


def summary(lang: str, form: dict) -> str:
    return t(lang, "form_confirm", **{k: form.get(k, "-") for k in ("name", "phone", "email", "request")})


async def start_form(session: AsyncSession, conversation: Conversation, lang: str) -> FormReply:
    _set(conversation, "name", {})
    await session.commit()
    return FormReply(t(lang, "form_name"))


async def cancel_form(session: AsyncSession, conversation: Conversation, lang: str) -> FormReply:
    _set(conversation, None, None)
    await session.commit()
    return FormReply(t(lang, "form_cancelled"), finished=True)


async def submit_form(
    session: AsyncSession, conversation: Conversation, user: TelegramUser, lang: str
) -> FormReply:
    from app.services.handoff import request_human_support

    form = dict((conversation.context or {}).get("form", {}))
    user.phone, user.email = form.get("phone"), form.get("email")
    if form.get("name"):
        user.full_name = form["name"]
    _set(conversation, None, None)
    conversation.context = {**conversation.context, "request": form}
    await request_human_support(session, conversation, note=form.get("request", ""))
    await logs.activity(session, "Contact form sent", record_id=conversation.id, details=form.get("request", ""))
    return FormReply(t(lang, "form_done"), finished=True)


async def handle_form_input(
    session: AsyncSession, conversation: Conversation, user: TelegramUser, text: str
) -> FormReply:
    """One answer from the user while a form is open."""
    lang = user.language
    word = normalize(text)
    if word in CANCEL_WORDS or text.strip().lower() == "/cancel":
        return await cancel_form(session, conversation, lang)

    step = conversation.session_step or STEPS[0]
    form = dict((conversation.context or {}).get("form", {}))

    if step == "confirm":
        if word in YES_WORDS:
            return await submit_form(session, conversation, user, lang)
        if word in NO_WORDS:
            return await cancel_form(session, conversation, lang)
        return FormReply(t(lang, "form_yes_no") + "\n\n" + summary(lang, form), confirm=True)

    value = VALIDATORS[step](text)
    if value is None:
        return FormReply(t(lang, f"form_invalid_{step}"))
    form[step] = value
    next_step = STEPS[STEPS.index(step) + 1]
    _set(conversation, next_step, form)
    await session.commit()
    if next_step == "confirm":
        return FormReply(summary(lang, form), confirm=True)
    return FormReply(t(lang, f"form_{next_step}"))
