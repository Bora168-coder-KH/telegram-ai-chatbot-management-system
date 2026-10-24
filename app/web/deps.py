"""Shared helpers for the dashboard routes: templates, database session, login and permissions.

Login state lives in a signed session cookie (Starlette SessionMiddleware):
  session["admin_id"]   who is logged in
  session["last_seen"]  for Auto Logout after SESSION_TIMEOUT_MINUTES without activity
  session["csrf"]       token every POST/DELETE must send back (X-CSRF-Token header or csrf_token field)
"""
import secrets
import time
from pathlib import Path
from urllib.parse import quote

from fastapi import Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.db import SessionLocal
from app.models import Admin, Conversation
from app.services import masking
from app.services.handoff import ACTIVE

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# (label, path, permission needed to see it)
NAV = [
    ("Dashboard", "/dashboard", "view"),
    ("Users", "/users", "view"),
    ("Conversations", "/conversations", "view"),
    ("FAQ", "/faq", "view"),
    ("Knowledge Base", "/knowledge", "view"),
    ("Intents", "/intents", "view"),
    ("Commands", "/commands", "view"),
    ("Broadcast", "/broadcast", "broadcast"),
    ("Reports", "/reports", "report"),
    ("Settings", "/settings", "edit"),
    ("Logs", "/logs", "report"),
]


class LoginRequired(Exception):
    """Raised by `current_admin`; main.py turns it into a redirect to /login."""

    def __init__(self, next_url: str = "/dashboard"):
        self.next_url = next_url


async def get_session():
    async with SessionLocal() as session:
        yield session


def csrf_token(request: Request) -> str:
    token = request.session.get("csrf")
    if not token:
        token = request.session["csrf"] = secrets.token_urlsafe(24)
    return token


async def check_csrf(request: Request) -> None:
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return
    sent = request.headers.get("x-csrf-token")
    if not sent and request.headers.get("content-type", "").startswith(
        ("application/x-www-form-urlencoded", "multipart/form-data")
    ):
        sent = (await request.form()).get("csrf_token")
    expected = request.session.get("csrf")
    if not expected or not isinstance(sent, str) or not secrets.compare_digest(sent, expected):
        raise HTTPException(status_code=403, detail="Invalid or missing CSRF token. Reload the page and try again.")


async def current_admin(request: Request, session: AsyncSession = Depends(get_session)) -> Admin:
    admin_id = request.session.get("admin_id")
    last_seen = request.session.get("last_seen", 0)
    next_url = quote(request.url.path)
    if not admin_id:
        raise LoginRequired(next_url)
    if time.time() - last_seen > settings.session_timeout_minutes * 60:
        request.session.clear()  # Auto Logout
        request.session["flash"] = "You were logged out after a period of inactivity."
        raise LoginRequired(next_url)
    admin = (await session.execute(
        select(Admin).where(Admin.id == admin_id).options(selectinload(Admin.role))
    )).scalar_one_or_none()
    if admin is None or admin.status != "Active":
        request.session.clear()
        raise LoginRequired(next_url)
    await check_csrf(request)
    request.session["last_seen"] = int(time.time())
    return admin


def can(admin: Admin | None, permission: str) -> bool:
    return bool(admin and admin.role and permission in (admin.role.permissions or []))


def require(permission: str):
    """Route dependency: the logged-in admin must have this permission."""
    async def dependency(admin: Admin = Depends(current_admin)) -> Admin:
        if not can(admin, permission):
            raise HTTPException(status_code=403, detail=f"Your role cannot do this (needs '{permission}').")
        return admin
    return dependency


async def queue_count(session: AsyncSession) -> int:
    query = select(func.count(Conversation.id)).where(Conversation.support_status.in_(ACTIVE))
    return (await session.execute(query)).scalar_one()


async def render(
    request: Request, name: str, admin: Admin | None, session: AsyncSession | None = None,
    active: str = "", **context,
):
    nav = [(label, href) for label, href, permission in NAV if can(admin, permission)]
    show_pii = masking.can_see_personal_data(admin)
    return templates.TemplateResponse(request, name, {
        "nav": nav, "active": active, "admin": admin, "can": lambda p: can(admin, p),
        "csrf": csrf_token(request), "queue_count": await queue_count(session) if session else 0,
        "show_pii": show_pii, "flash": request.session.pop("flash", None), **context,
    })


def partial(request: Request, name: str, admin: Admin | None = None, **context):
    """An HTMX fragment (no layout)."""
    return templates.TemplateResponse(request, name, {
        "admin": admin, "can": lambda p: can(admin, p), "csrf": csrf_token(request),
        "show_pii": masking.can_see_personal_data(admin), **context,
    })
