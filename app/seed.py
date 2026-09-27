"""Sample data so the bot and dashboard work on day one.

Run:  python -m app.seed
It is safe to run more than once (it only adds data if the tables are empty).
"""
import asyncio

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal, init_db
from app.models import FAQ, Bot, Command, KnowledgeArticle, Role

ROLES = {
    "Administrator": ["view", "create", "edit", "delete", "reply", "broadcast", "train", "report"],
    "Bot Manager": ["view", "create", "edit", "delete", "broadcast", "report"],
    "Content Manager": ["view", "create", "edit", "delete", "train"],
    "Support Agent": ["view", "edit", "reply"],
    "Viewer": ["view", "report"],
}


async def _empty(session: AsyncSession, model) -> bool:
    return (await session.execute(select(func.count()).select_from(model))).scalar_one() == 0


async def seed_defaults(session: AsyncSession) -> None:
    if await _empty(session, Bot):
        session.add(Bot(
            name="AI Chatbot",
            welcome_message="Welcome!",
            support_contact="support@example.com",
            system_prompt=(
                "You are a helpful support assistant. Answer briefly and politely in the "
                "user's language (Khmer or English). Only answer topics related to our "
                "services. If you are not sure, say so."
            ),
        ))
    if await _empty(session, Role):
        for name, permissions in ROLES.items():
            session.add(Role(name=name, permissions=permissions))
    if await _empty(session, Command):
        session.add(Command(
            name="contact",
            description="Show contact information",
            response="You can reach us at support@example.com",
        ))
    if await _empty(session, FAQ):
        session.add_all([
            FAQ(question="What are your opening hours?",
                answer="We are open Monday to Friday, 8:00 to 17:00.",
                category="General", keywords="opening hours,open,office hours", language="en"),
            FAQ(question="How do I register?",
                answer="You can register by choosing Registration in the menu or visiting our office.",
                category="Registration", keywords="register,registration,sign up", language="en"),
            FAQ(question="ម៉ោងបើកទ្វាររបស់អ្នកគឺម៉ោងប៉ុន្មាន?",
                answer="យើងបើកពីថ្ងៃច័ន្ទដល់ថ្ងៃសុក្រ ម៉ោង ៨:០០ ដល់ ១៧:០០។",
                category="General", keywords="ម៉ោងបើក,ម៉ោងធ្វើការ", language="km"),
        ])
    if await _empty(session, KnowledgeArticle):
        session.add(KnowledgeArticle(
            title="Refund policy",
            category="Payment",
            content="Refunds are possible within 7 days of payment. Please contact support with your receipt.",
            keywords="refund,money back,cancel payment",
            language="en",
        ))
    await session.commit()


async def main() -> None:
    await init_db()
    async with SessionLocal() as session:
        await seed_defaults(session)
    print("Seed data ready.")


if __name__ == "__main__":
    asyncio.run(main())
