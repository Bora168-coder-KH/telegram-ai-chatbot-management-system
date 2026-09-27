"""Response Routing Logic.

    Command -> Keyword / Rule -> FAQ -> Knowledge Base -> AI -> Fallback -> Human Handoff

Commands (/start, /help, /menu and custom commands) are detected by the bot layer
before this function is called. `route_message()` handles everything after that.
"""
import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.i18n import t
from app.models import FAQ, Bot, KnowledgeArticle, Source, TelegramUser, UnknownQuestion, utcnow
from app.services import ai
from app.services.rules import match_rule

FAQ_MIN_SCORE = 0.6


@dataclass
class Reply:
    text: str
    source: str  # one of models.Source
    fallback: bool = False


def normalize(text: str) -> str:
    """Lowercase, remove punctuation, collapse spaces."""
    text = re.sub(r"[^\w\s]", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def keyword_list(keywords: str) -> list[str]:
    return [normalize(k) for k in keywords.split(",") if normalize(k)]


def faq_score(text: str, faq: FAQ) -> float:
    """0..1 score: similar question OR a keyword found in the message."""
    norm = normalize(text)
    score = SequenceMatcher(None, norm, normalize(faq.question)).ratio()
    if any(k in norm for k in keyword_list(faq.keywords)):
        score = max(score, 0.9)
    return score


async def find_faq(session: AsyncSession, text: str, language: str) -> FAQ | None:
    result = await session.execute(select(FAQ).where(FAQ.status == "Active"))
    best, best_score = None, 0.0
    for faq in result.scalars():
        score = faq_score(text, faq)
        if faq.language == language:
            score += 0.01  # prefer the user's language when scores are close
        score += faq.priority * 0.001
        if score > best_score:
            best, best_score = faq, score
    return best if best is not None and best_score >= FAQ_MIN_SCORE else None


async def find_article(session: AsyncSession, text: str, language: str) -> KnowledgeArticle | None:
    norm = normalize(text)
    result = await session.execute(
        select(KnowledgeArticle).where(KnowledgeArticle.status == "Published")
    )
    best, best_hits = None, 0
    for article in result.scalars():
        hits = sum(1 for k in keyword_list(article.keywords) if k in norm)
        if hits and article.language == language:
            hits += 0.5
        if hits > best_hits:
            best, best_hits = article, hits
    return best


async def save_unknown_question(session: AsyncSession, text: str) -> None:
    """Unknown Question Detection: remember what the bot could not answer."""
    norm = normalize(text)
    if not norm:
        return
    result = await session.execute(select(UnknownQuestion).where(UnknownQuestion.question == norm))
    unknown = result.scalar_one_or_none()
    if unknown is None:
        session.add(UnknownQuestion(question=norm))
    else:
        unknown.frequency += 1
        unknown.last_asked_at = utcnow()
    await session.commit()


async def route_message(session: AsyncSession, user: TelegramUser, text: str) -> Reply:
    lang = user.language

    # 1. Keyword / rule-based response
    rule_answer = match_rule(text, lang)
    if rule_answer:
        return Reply(rule_answer, Source.RULE)

    # 2. FAQ
    faq = await find_faq(session, text, lang)
    if faq:
        return Reply(faq.answer, Source.FAQ)

    # 3. Knowledge Base (+ AI if configured)
    article = await find_article(session, text, lang)
    bot = (await session.execute(select(Bot))).scalars().first()
    system_prompt = bot.system_prompt if bot else ""
    if article:
        if ai.ai_enabled():
            answer = await ai.generate_answer(text, article.content, system_prompt, lang)
            if answer:
                return Reply(answer, Source.AI)
        return Reply(article.content, Source.KNOWLEDGE)

    # 4. AI without Knowledge Base context
    answer = await ai.generate_answer(text, "", system_prompt, lang)
    if answer:
        return Reply(answer, Source.AI)

    # 5. Fallback (+ remember the unknown question)
    await save_unknown_question(session, text)
    fallback_text = bot.fallback_message if bot and bot.fallback_message else t(lang, "fallback")
    return Reply(fallback_text, Source.FALLBACK, fallback=True)
