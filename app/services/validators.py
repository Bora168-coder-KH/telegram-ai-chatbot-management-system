"""Input validation and entity extraction (phone, email, date, number).

Each `valid_*` function returns the cleaned value, or None if the input is invalid.
The same patterns are used to pull entities out of a free-text message.
"""
import re
from datetime import date, datetime

# Khmer digits are converted to Latin digits before checking.
_KHMER_DIGITS = str.maketrans("០១២៣៤៥៦៧៨៩", "0123456789")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Cambodian numbers: 0XX XXX XXX(X) or +855 XX XXX XXX(X), spaces/dashes allowed
PHONE_RE = re.compile(r"(?:\+?855[\s-]?|0)(?:\d[\s-]?){7,9}\d")
DATE_RE = re.compile(r"\b(\d{4}-\d{1,2}-\d{1,2}|\d{1,2}/\d{1,2}/\d{4})\b")
NUMBER_RE = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?(?![\w.])")
_DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y")


def _latin(text: str) -> str:
    return text.translate(_KHMER_DIGITS).strip()


def valid_email(text: str) -> str | None:
    text = text.strip()
    return text.lower() if EMAIL_RE.fullmatch(text) else None


def valid_phone(text: str) -> str | None:
    """Returns the phone in local form, digits only: 012345678."""
    text = _latin(text)
    if not PHONE_RE.fullmatch(text):
        return None
    digits = re.sub(r"\D", "", text)
    if digits.startswith("855"):
        digits = "0" + digits[3:]
    return digits if 9 <= len(digits) <= 10 else None


def valid_date(text: str) -> date | None:
    text = _latin(text)
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


def valid_number(text: str) -> float | None:
    text = _latin(text).replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None


def valid_name(text: str) -> str | None:
    """2-100 characters, at least two letters, no digits."""
    text = " ".join(text.split())
    if not 2 <= len(text) <= 100 or any(ch.isdigit() for ch in text):
        return None
    return text if sum(ch.isalpha() for ch in text) >= 2 else None


def extract_entities(text: str, kinds: list[str] | None = None) -> dict[str, str]:
    """Find phone, email, date and number entities in a message.

    Returns {kind: value as text}. Only the first match of each kind is kept.
    """
    kinds = kinds or ["email", "phone", "date", "number"]
    latin = _latin(text)
    found: dict[str, str] = {}
    if "email" in kinds and (m := EMAIL_RE.search(text)):
        found["email"] = m.group().lower()
    if "phone" in kinds:
        for m in PHONE_RE.finditer(latin):
            if phone := valid_phone(m.group()):
                found["phone"] = phone
                break
    if "date" in kinds:
        for m in DATE_RE.finditer(latin):
            if day := valid_date(m.group()):
                found["date"] = day.isoformat()
                break
    if "number" in kinds:
        # numbers that are not part of a phone or date already found
        rest = latin
        for value in (m.group() for m in DATE_RE.finditer(latin)):
            rest = rest.replace(value, " ")
        for m in PHONE_RE.finditer(rest):
            rest = rest.replace(m.group(), " ")
        if m := NUMBER_RE.search(rest):
            found["number"] = m.group()
    return found


def scrub_contacts(text: str) -> str:
    """Replace emails and phone numbers with [email] / [phone] (for question statistics)."""
    text = EMAIL_RE.sub("[email]", text)
    return PHONE_RE.sub("[phone]", _latin(text))
