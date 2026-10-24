"""Text helpers shared by FAQ, Knowledge Base and intent matching."""
import re
import unicodedata


def normalize(text: str) -> str:
    """Lowercase, remove punctuation, collapse spaces.

    Keeps letters, numbers and combining marks: Khmer vowel signs are marks, and
    removing them would break Khmer words apart.
    """
    text = "".join(
        ch if ch.isspace() or unicodedata.category(ch)[0] in "LMN" else " " for ch in text.lower()
    )
    return re.sub(r"\s+", " ", text).strip()


def keyword_list(keywords: str) -> list[str]:
    return [normalize(k) for k in keywords.split(",") if normalize(k)]
