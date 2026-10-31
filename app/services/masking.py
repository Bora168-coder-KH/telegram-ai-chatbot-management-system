"""Data masking for Telegram user data, by role.

Only roles with the "reply" permission (Administrator, Support Agent) talk to
users, so only they see full names, usernames, phone numbers and emails. Other
roles (Bot Manager, Content Manager, Viewer) see masked values on every page and
in every export.
"""
from app.services.validators import EMAIL_RE, PHONE_RE

PII_PERMISSION = "reply"


def can_see_personal_data(admin) -> bool:
    role = getattr(admin, "role", None)
    return bool(role and PII_PERMISSION in (role.permissions or []))


def _word(word: str) -> str:
    return word[:1] + "*" * max(len(word) - 1, 2)


def mask_name(name: str | None) -> str:
    if not name:
        return "-"
    return " ".join(_word(w) for w in name.split())


def mask_username(username: str | None) -> str:
    return "@" + _word(username) if username else "-"


def mask_phone(phone: str | None) -> str:
    if not phone:
        return "-"
    return phone[:3] + "*" * max(len(phone) - 6, 3) + phone[-3:] if len(phone) > 6 else "*" * len(phone)


def mask_email(email: str | None) -> str:
    if not email or "@" not in email:
        return "-"
    local, domain = email.split("@", 1)
    return _word(local) + "@" + domain


def mask_telegram_id(telegram_id: int | None) -> str:
    text = str(telegram_id or "")
    return text[:2] + "*" * max(len(text) - 4, 2) + text[-2:] if len(text) > 4 else "****"


MASKERS = {
    "name": mask_name, "username": mask_username, "phone": mask_phone,
    "email": mask_email, "telegram_id": mask_telegram_id,
}


def pii(value, kind: str, show: bool) -> str:
    """Jinja filter: {{ user.phone | pii("phone", show_pii) }}"""
    if show:
        if kind == "username":
            return "@" + value if value else "-"
        return str(value) if value not in (None, "") else "-"
    return MASKERS[kind](value)


def mask_text(text: str | None, show: bool) -> str:
    """Jinja filter for free text (messages): hide phone numbers and emails the user typed."""
    if show or not text:
        return text or ""
    text = EMAIL_RE.sub(lambda m: mask_email(m.group()), text)
    return PHONE_RE.sub(lambda m: mask_phone(m.group().replace(" ", "").replace("-", "")), text)
