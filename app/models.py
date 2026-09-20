"""Data models (16 from the assignment + UnknownQuestion).

Model names follow the ERD in the project documentation. The Telegram end user is
called TelegramUser here so it does not clash with admin users.
"""
from datetime import datetime, timezone

from sqlalchemy import JSON, BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ---- Allowed values (kept as plain strings to stay simple) -------------------
class UserStatus:
    ACTIVE, INACTIVE, BLOCKED, SUSPENDED = "Active", "Inactive", "Blocked", "Suspended"


class SupportStatus:
    OPEN, ASSIGNED, IN_PROGRESS, RESOLVED, CLOSED = (
        "Open", "Assigned", "In Progress", "Resolved", "Closed",
    )


class Source:
    """Where a response came from (Message.response_source)."""
    COMMAND, RULE, FAQ, KNOWLEDGE, AI, FALLBACK, AGENT = (
        "Command", "Rule", "FAQ", "KnowledgeBase", "AI", "Fallback", "Agent",
    )


# ---- Admin side --------------------------------------------------------------
class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    # e.g. ["view", "create", "edit", "delete", "reply", "broadcast", "train", "report"]
    permissions: Mapped[list] = mapped_column(JSON, default=list)


class Admin(Base):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    status: Mapped[str] = mapped_column(String(20), default="Active")
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    role: Mapped[Role] = relationship()


class Agent(Base):
    __tablename__ = "agents"
    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id: Mapped[int] = mapped_column(ForeignKey("admins.id"), unique=True)
    availability: Mapped[str] = mapped_column(String(20), default="available")

    admin: Mapped[Admin] = relationship()


# ---- Bot configuration -------------------------------------------------------
class Bot(Base):
    """Bot settings. The Bot Token itself stays in .env, not in the database."""
    __tablename__ = "bots"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), default="AI Chatbot")
    username: Mapped[str] = mapped_column(String(100), default="")
    default_language: Mapped[str] = mapped_column(String(5), default="en")
    welcome_message: Mapped[str] = mapped_column(Text, default="")
    fallback_message: Mapped[str] = mapped_column(Text, default="")
    support_contact: Mapped[str] = mapped_column(String(200), default="")
    working_status: Mapped[str] = mapped_column(String(20), default="enabled")
    maintenance_mode: Mapped[bool] = mapped_column(default=False)
    # AI settings
    system_prompt: Mapped[str] = mapped_column(Text, default="")
    ai_model: Mapped[str] = mapped_column(String(100), default="")
    ai_temperature: Mapped[float] = mapped_column(default=0.3)
    ai_max_length: Mapped[int] = mapped_column(Integer, default=500)
    response_style: Mapped[str] = mapped_column(String(20), default="short")


class Command(Base):
    __tablename__ = "commands"
    id: Mapped[int] = mapped_column(primary_key=True)
    bot_id: Mapped[int] = mapped_column(ForeignKey("bots.id"), default=1)
    name: Mapped[str] = mapped_column(String(50), unique=True)  # without "/"
    description: Mapped[str] = mapped_column(String(200), default="")
    response: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="Active")
    permission: Mapped[str] = mapped_column(String(50), default="everyone")


# ---- Telegram users, conversations, messages ---------------------------------
class TelegramUser(Base):
    __tablename__ = "telegram_users"
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    full_name: Mapped[str] = mapped_column(String(200), default="")
    language: Mapped[str] = mapped_column(String(5), default="en")
    first_interaction_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    last_interaction_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    status: Mapped[str] = mapped_column(String(20), default=UserStatus.ACTIVE)


class Conversation(Base):
    __tablename__ = "conversations"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("telegram_users.id"), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    last_message_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    status: Mapped[str] = mapped_column(String(20), default="active")
    intent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    assigned_agent_id: Mapped[int | None] = mapped_column(ForeignKey("agents.id"), nullable=True)
    support_status: Mapped[str | None] = mapped_column(String(20), nullable=True)  # SupportStatus
    resolution_status: Mapped[str] = mapped_column(String(20), default="unresolved")
    # Conversation session: remembers where the user is in a multi-step form.
    session_step: Mapped[str | None] = mapped_column(String(50), nullable=True)
    context: Mapped[dict] = mapped_column(JSON, default=dict)


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("telegram_users.id"), index=True)
    direction: Mapped[str] = mapped_column(String(10))  # "incoming" or "outgoing"
    message_type: Mapped[str] = mapped_column(String(20), default="text")
    content: Mapped[str] = mapped_column(Text, default="")
    response_source: Mapped[str | None] = mapped_column(String(20), nullable=True)  # Source
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Feedback(Base):
    __tablename__ = "feedback"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("telegram_users.id"))
    message_id: Mapped[int | None] = mapped_column(ForeignKey("messages.id"), nullable=True)
    conversation_id: Mapped[int | None] = mapped_column(ForeignKey("conversations.id"), nullable=True)
    rating: Mapped[int] = mapped_column(Integer)  # 1-5 (thumbs up = 5, thumbs down = 1)
    comment: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


# ---- Knowledge ---------------------------------------------------------------
class Intent(Base):
    __tablename__ = "intents"
    id: Mapped[int] = mapped_column(primary_key=True)
    bot_id: Mapped[int] = mapped_column(ForeignKey("bots.id"), default=1)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    response: Mapped[str] = mapped_column(Text, default="")
    priority: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="Active")

    phrases: Mapped[list["TrainingPhrase"]] = relationship(back_populates="intent")


class TrainingPhrase(Base):
    __tablename__ = "training_phrases"
    id: Mapped[int] = mapped_column(primary_key=True)
    intent_id: Mapped[int] = mapped_column(ForeignKey("intents.id"))
    phrase: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(5), default="en")

    intent: Mapped[Intent] = relationship(back_populates="phrases")


class FAQ(Base):
    __tablename__ = "faqs"
    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50), default="General")
    keywords: Mapped[str] = mapped_column(Text, default="")  # comma separated
    language: Mapped[str] = mapped_column(String(5), default="en")
    priority: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="Active")


class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(50), default="General")
    content: Mapped[str] = mapped_column(Text)
    keywords: Mapped[str] = mapped_column(Text, default="")
    language: Mapped[str] = mapped_column(String(5), default="en")
    author_id: Mapped[int | None] = mapped_column(ForeignKey("admins.id"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    status: Mapped[str] = mapped_column(String(20), default="Published")


class UnknownQuestion(Base):
    """Questions the bot could not answer, for admin review (Unanswered Questions)."""
    __tablename__ = "unknown_questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(Text, unique=True)  # normalized text
    frequency: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(20), default="open")  # open / resolved
    last_asked_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


# ---- Broadcast and notifications ---------------------------------------------
class Broadcast(Base):
    __tablename__ = "broadcasts"
    id: Mapped[int] = mapped_column(primary_key=True)
    bot_id: Mapped[int] = mapped_column(ForeignKey("bots.id"), default=1)
    message: Mapped[str] = mapped_column(Text)
    audience: Mapped[str] = mapped_column(String(20), default="all")  # all / active / selected
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    delivery_result: Mapped[dict] = mapped_column(JSON, default=dict)
    sent_by: Mapped[int | None] = mapped_column(ForeignKey("admins.id"), nullable=True)


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("telegram_users.id"))
    broadcast_id: Mapped[int | None] = mapped_column(ForeignKey("broadcasts.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(30))  # Welcome, Reminder, Announcement, ...
    content: Mapped[str] = mapped_column(Text, default="")
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    delivery_status: Mapped[str] = mapped_column(String(20), default="pending")


# ---- Logs --------------------------------------------------------------------
class Log(Base):
    __tablename__ = "logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    log_type: Mapped[str] = mapped_column(String(20))  # Activity, Conversation, Audit, Error
    actor: Mapped[str] = mapped_column(String(100), default="system")
    action: Mapped[str] = mapped_column(String(200), default="")
    record_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    details: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
