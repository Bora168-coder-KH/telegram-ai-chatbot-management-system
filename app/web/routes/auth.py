"""Admin login and logout."""
import time

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Admin, utcnow
from app.services import logs
from app.services.auth import verify_password
from app.web.deps import check_csrf, get_session, templates, csrf_token

router = APIRouter()

MAX_FAILURES, LOCK_SECONDS = 5, 15 * 60
_failures: dict[str, list[float]] = {}  # email -> times of failed logins (in memory, prototype)


def _locked(email: str) -> bool:
    recent = [t for t in _failures.get(email, []) if time.time() - t < LOCK_SECONDS]
    _failures[email] = recent
    return len(recent) >= MAX_FAILURES


def _safe_next(url: str) -> str:
    return url if url.startswith("/") and not url.startswith("//") else "/dashboard"


def _page(request: Request, error: str = "", email: str = "", next_url: str = "/dashboard", status: int = 200):
    return templates.TemplateResponse(request, "login.html", {
        "error": error, "email": email, "next": next_url, "csrf": csrf_token(request),
        "flash": request.session.pop("flash", None),
    }, status_code=status)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = "/dashboard"):
    if request.session.get("admin_id"):
        return RedirectResponse(_safe_next(next), status_code=303)
    return _page(request, next_url=_safe_next(next))


@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form("/dashboard"),
    session: AsyncSession = Depends(get_session),
):
    await check_csrf(request)
    email = email.strip().lower()
    if _locked(email):
        return _page(request, "Too many failed attempts. Try again in 15 minutes.", email, next, 429)
    admin = (await session.execute(select(Admin).where(Admin.email == email))).scalar_one_or_none()
    if admin is None or admin.status != "Active" or not verify_password(password, admin.password_hash):
        _failures.setdefault(email, []).append(time.time())
        await logs.audit(session, email, "Failed login")
        return _page(request, "Wrong email or password.", email, next, 401)
    _failures.pop(email, None)
    request.session.clear()  # new session id data after login
    request.session.update(admin_id=admin.id, last_seen=int(time.time()))
    admin.last_login_at = utcnow()
    await logs.audit(session, admin.email, "Login", record_id=admin.id)
    return RedirectResponse(_safe_next(next), status_code=303)


@router.post("/logout")
async def logout(request: Request, session: AsyncSession = Depends(get_session)):
    await check_csrf(request)
    admin_id = request.session.get("admin_id")
    if admin_id and (admin := await session.get(Admin, admin_id)):
        await logs.audit(session, admin.email, "Logout", record_id=admin.id)
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
