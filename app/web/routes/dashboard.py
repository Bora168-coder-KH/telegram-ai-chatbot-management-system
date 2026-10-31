"""Dashboard (statistics, KPIs, charts) and Users."""
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Admin, TelegramUser, UnknownQuestion, UserStatus
from app.services import logs
from app.services.stats import chart_data, dashboard_stats
from app.web.deps import get_session, partial, render, require

router = APIRouter()
STATUSES = [UserStatus.ACTIVE, UserStatus.INACTIVE, UserStatus.BLOCKED, UserStatus.SUSPENDED]


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, admin: Admin = Depends(require("view")),
                    session: AsyncSession = Depends(get_session)):
    stats = await dashboard_stats(session)
    unknown = (await session.execute(
        select(UnknownQuestion).where(UnknownQuestion.status == "open")
        .order_by(UnknownQuestion.frequency.desc()).limit(10)
    )).scalars().all()
    return await render(request, "dashboard.html", admin, session, "Dashboard",
                        stats=stats, unknown=unknown, charts=await chart_data(session))


@router.post("/unknown/{question_id}/resolve", response_class=HTMLResponse)
async def resolve_unknown(question_id: int, admin: Admin = Depends(require("train")),
                          session: AsyncSession = Depends(get_session)):
    """Mark an unanswered question as handled (e.g. after adding a FAQ for it)."""
    question = await session.get(UnknownQuestion, question_id)
    if question:
        question.status = "resolved"
        await logs.audit(session, admin.email, "Resolved unanswered question", question.id, question.question)
    return HTMLResponse("")


@router.get("/users", response_class=HTMLResponse)
async def users(request: Request, q: str = "", status: str = "", admin: Admin = Depends(require("view")),
                session: AsyncSession = Depends(get_session)):
    query = select(TelegramUser).order_by(TelegramUser.id.desc())
    if q:
        like = f"%{q}%"
        query = query.where(or_(TelegramUser.full_name.ilike(like), TelegramUser.username.ilike(like),
                                TelegramUser.phone.ilike(like), TelegramUser.email.ilike(like)))
    if status in STATUSES:
        query = query.where(TelegramUser.status == status)
    rows = (await session.execute(query.limit(200))).scalars().all()
    return await render(request, "users.html", admin, session, "Users", users=rows, q=q, status=status,
                        statuses=STATUSES)


@router.post("/users/{user_id}/status", response_class=HTMLResponse)
async def set_user_status(request: Request, user_id: int, status: str = Form(...),
                          admin: Admin = Depends(require("edit")), session: AsyncSession = Depends(get_session)):
    """HTMX: change a user's status (Active / Inactive / Blocked / Suspended)."""
    user = await session.get(TelegramUser, user_id)
    if user and status in STATUSES and status != user.status:
        old, user.status = user.status, status
        await logs.audit(session, admin.email, "Changed user status", user.id, f"{old} -> {status}")
    return partial(request, "_user_row.html", admin, u=user, statuses=STATUSES)
