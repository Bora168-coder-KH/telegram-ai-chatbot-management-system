"""Intent detection with training phrases, plus entity extraction.

An intent matches when the message is similar to one of its training phrases
(difflib ratio), or when every word of a training phrase appears in the message.
Entities listed on the intent (phone, email, date, number) are pulled out of the
message and can be used in the response, e.g. "We noted the date {date}."
"""
from dataclasses import dataclass, field
from difflib import SequenceMatcher

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Intent
from app.services.text import normalize
from app.services.validators import extract_entities

INTENT_MIN_SCORE = 0.75


@dataclass
class IntentMatch:
    intent: Intent
    score: float
    entities: dict[str, str] = field(default_factory=dict)

    def response(self) -> str:
        """The intent's response with entity placeholders filled in ("-" if missing)."""
        values = {kind: self.entities.get(kind, "-") for kind in ("phone", "email", "date", "number")}
        try:
            return self.intent.response.format_map(values)
        except (KeyError, ValueError, IndexError):
            return self.intent.response


def phrase_score(text: str, phrase: str) -> float:
    norm, target = normalize(text), normalize(phrase)
    if not norm or not target:
        return 0.0
    score = SequenceMatcher(None, norm, target).ratio()
    words = target.split()
    if len(words) >= 2 and all(w in norm.split() for w in words):
        score = max(score, 0.85)  # every word of the phrase is in the message
    elif " " not in target and len(target) >= 4 and target in norm:
        score = max(score, 0.8)  # Khmer has no spaces between words: substring match
    return score


async def detect_intent(session: AsyncSession, text: str, language: str) -> IntentMatch | None:
    result = await session.execute(
        select(Intent).where(Intent.status == "Active").options(selectinload(Intent.phrases))
    )
    best: IntentMatch | None = None
    for intent in result.scalars():
        for phrase in intent.phrases:
            score = phrase_score(text, phrase.phrase)
            if phrase.language == language:
                score += 0.01
            score += intent.priority * 0.001
            if best is None or score > best.score:
                best = IntentMatch(intent, score)
    if best is None or best.score < INTENT_MIN_SCORE:
        return None
    best.entities = extract_entities(text, best.intent.entities) if best.intent.entities else {}
    return best
