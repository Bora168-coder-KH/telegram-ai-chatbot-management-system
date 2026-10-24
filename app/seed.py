"""Sample data so the bot and dashboard work on day one.

Run:  python -m app.seed
It is safe to run more than once (it only adds data if the tables are empty).
"""
import asyncio
import logging
import os
import secrets

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import SessionLocal, init_db
from app.models import FAQ, Admin, Agent, Bot, Command, Intent, KnowledgeArticle, Role, TrainingPhrase
from app.services.auth import hash_password

logger = logging.getLogger(__name__)

ROLES = {
    "Administrator": ["view", "create", "edit", "delete", "reply", "broadcast", "train", "report"],
    "Bot Manager": ["view", "create", "edit", "delete", "broadcast", "report"],
    "Content Manager": ["view", "create", "edit", "delete", "train"],
    "Support Agent": ["view", "edit", "reply"],
    "Viewer": ["view", "report"],
}

# name -> (description, response, entities, priority, [(phrase, language)])
INTENTS = {
    "contact_request": (
        "Start the contact form (Name -> Phone -> Email -> Request)",
        "", [], 10,
        [("I want to send a request", "en"), ("I need to contact staff", "en"),
         ("I want to make a request", "en"), ("please contact me", "en"),
         ("ខ្ញុំចង់ដាក់សំណើ", "km"), ("សូមទាក់ទងខ្ញុំ", "km")],
    ),
    "book_appointment": (
        "User wants an appointment; extracts the date",
        "Thank you! We noted your appointment request for {date}. Our team will confirm it soon. "
        "If the date shows '-', please send it as 2026-11-02 or 02/11/2026.",
        ["date"], 5,
        [("I want to book an appointment", "en"), ("book a meeting", "en"),
         ("can I make an appointment", "en"), ("schedule a visit", "en"),
         ("ខ្ញុំចង់ណាត់ជួប", "km")],
    ),
    "check_request_status": (
        "User asks about the status of a request",
        "You can see the status of your request with the Human Support button. "
        "An agent will reply in this chat as soon as possible.",
        [], 0,
        [("what is the status of my request", "en"), ("check my request status", "en"),
         ("any update on my request", "en"), ("តើសំណើរបស់ខ្ញុំយ៉ាងម៉េចហើយ", "km")],
    ),
}

PASSWORD_FILE = "admin-password.txt"  # git-ignored


def _generated_password() -> str:
    """No ADMIN_PASSWORD in .env: make one and write it to a file only the owner can read."""
    password = secrets.token_urlsafe(12)
    try:
        fd = os.open(PASSWORD_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(f"{settings.admin_email}\n{password}\n")
        logger.warning("Created admin %s; the initial password is in %s (delete the file after you log in, "
                       "or set ADMIN_PASSWORD in .env)", settings.admin_email, PASSWORD_FILE)
    except OSError:
        logger.error("Created admin %s but could not write %s; set ADMIN_PASSWORD in .env and reset the "
                     "admins table", settings.admin_email, PASSWORD_FILE)
    return password


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
    await session.flush()
    if await _empty(session, Admin):
        password = settings.admin_password or _generated_password()
        role = (await session.execute(select(Role).where(Role.name == "Administrator"))).scalar_one()
        admin = Admin(name="Administrator", email=settings.admin_email, password_hash=hash_password(password),
                      role_id=role.id)
        session.add(admin)
        await session.flush()
        session.add(Agent(admin_id=admin.id))  # the first admin can also answer support requests
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
                category="Registration", keywords="how do i register,how to register,how can i register", language="en"),
            FAQ(question="ម៉ោងបើកទ្វាររបស់អ្នកគឺម៉ោងប៉ុន្មាន?",
                answer="យើងបើកពីថ្ងៃច័ន្ទដល់ថ្ងៃសុក្រ ម៉ោង ៨:០០ ដល់ ១៧:០០។",
                category="General", keywords="ម៉ោងបើក,ម៉ោងធ្វើការ", language="km"),
        ])
    if await _empty(session, Intent):
        for name, (description, response, entities, priority, phrases) in INTENTS.items():
            session.add(Intent(
                name=name, description=description, response=response, entities=entities, priority=priority,
                phrases=[TrainingPhrase(phrase=p, language=lang) for p, lang in phrases],
            ))
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
