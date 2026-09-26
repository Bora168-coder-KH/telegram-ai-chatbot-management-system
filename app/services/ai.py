"""AI response generation (prototype hook).

The routing service calls `generate_answer()` only after Command, Rule, FAQ and
Knowledge Base did not fully answer the question.

TODO (learning task): connect a real LLM provider.
  1. Pick a provider and put its key in .env as AI_API_KEY (and AI_MODEL).
  2. Build the prompt: system prompt (role, tone, language, allowed topics, safety
     rules) + Knowledge Base context + the user's question.
  3. Call the provider with httpx (or its Python SDK), with a timeout and retry.
  4. Validate the result and return the text. Return None on any error so the
     router falls back gracefully.
"""
import logging

from app.config import settings

logger = logging.getLogger(__name__)


def ai_enabled() -> bool:
    return bool(settings.ai_api_key)


async def generate_answer(question: str, context: str, system_prompt: str, language: str) -> str | None:
    if not ai_enabled():
        return None
    logger.warning("AI_API_KEY is set but generate_answer() is not implemented yet.")
    return None
