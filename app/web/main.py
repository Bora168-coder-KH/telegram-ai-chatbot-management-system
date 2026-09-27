"""Admin dashboard (FastAPI + Jinja2 + HTMX).

Run:  uvicorn app.web.main:app --reload
Open: http://127.0.0.1:8000

TODO (team tasks): admin login + roles/permissions, Conversations, Knowledge Base,
Intents, Broadcast, Reports, Settings pages.
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal, init_db
from app.models import FAQ, TelegramUser, UnknownQuestion, UserStatus
from app.seed import seed_defaults
from app.services.stats import dashboard_stats

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

FAQ_CATEGORIES = ["General", "Account", "Service", "Payment", "Course", "Registration", "Technical Support"]

# Navigation: Dashboard -> Users -> Conversations -> FAQ -> Knowledge Base -> Broadcast -> Reports -> Settings
NAV = [
    ("Dashboard", "/dashboard"),
    ("Users", "/users"),
    ("Conversations", None),
    ("FAQ", "/faq"),
    ("Knowledge Base", None),
    ("Broadcast", None),
    ("Reports", None),
    ("Settings", None),
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with SessionLocal() as session:
        await seed_defaults(session)
    yield


app = FastAPI(title="AI Chatbot Management System", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


async def get_session():
    async with SessionLocal() as session:
        yield session


def render(request: Request, name: str, active: str = "", **context):
    return templates.TemplateResponse(request, name, {"nav": NAV, "active": active, **context})


@app.get("/")
async def index():
    return RedirectResponse("/dashboard")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, session: AsyncSession = Depends(get_session)):
    stats = await dashboard_stats(session)
    unknown = (
        await session.execute(
            select(UnknownQuestion)
            .where(UnknownQuestion.status == "open")
            .order_by(UnknownQuestion.frequency.desc())
            .limit(5)
        )
    ).scalars().all()
    return render(request, "dashboard.html", "Dashboard", stats=stats, unknown=unknown)


@app.get("/users", response_class=HTMLResponse)
async def users(request: Request, q: str = "", session: AsyncSession = Depends(get_session)):
    query = select(TelegramUser).order_by(TelegramUser.id.desc())
    if q:
        like = f"%{q}%"
        query = query.where(TelegramUser.full_name.ilike(like) | TelegramUser.username.ilike(like))
    rows = (await session.execute(query.limit(100))).scalars().all()
    return render(request, "users.html", "Users", users=rows, q=q, statuses=[
        UserStatus.ACTIVE, UserStatus.INACTIVE, UserStatus.BLOCKED, UserStatus.SUSPENDED,
    ])


@app.post("/users/{user_id}/status", response_class=HTMLResponse)
async def set_user_status(
    request: Request, user_id: int, status: str = Form(...), session: AsyncSession = Depends(get_session)
):
    """HTMX: change a user's status (Active / Inactive / Blocked / Suspended)."""
    user = await session.get(TelegramUser, user_id)
    if user and status in (UserStatus.ACTIVE, UserStatus.INACTIVE, UserStatus.BLOCKED, UserStatus.SUSPENDED):
        user.status = status
        await session.commit()
    return templates.TemplateResponse(request, "_user_row.html", {"u": user, "statuses": [
        UserStatus.ACTIVE, UserStatus.INACTIVE, UserStatus.BLOCKED, UserStatus.SUSPENDED,
    ]})


@app.get("/faq", response_class=HTMLResponse)
async def faq_page(request: Request, session: AsyncSession = Depends(get_session)):
    faqs = (await session.execute(select(FAQ).order_by(FAQ.id.desc()))).scalars().all()
    return render(request, "faq.html", "FAQ", faqs=faqs, categories=FAQ_CATEGORIES)


@app.post("/faq", response_class=HTMLResponse)
async def faq_create(
    request: Request,
    question: str = Form(...),
    answer: str = Form(...),
    category: str = Form("General"),
    keywords: str = Form(""),
    language: str = Form("en"),
    session: AsyncSession = Depends(get_session),
):
    """HTMX: add a FAQ and return only the new table row."""
    faq = FAQ(question=question.strip(), answer=answer.strip(), category=category,
              keywords=keywords.strip(), language=language)
    session.add(faq)
    await session.commit()
    return templates.TemplateResponse(request, "_faq_row.html", {"f": faq})


@app.delete("/faq/{faq_id}", response_class=HTMLResponse)
async def faq_delete(faq_id: int, session: AsyncSession = Depends(get_session)):
    faq = await session.get(FAQ, faq_id)
    if faq:
        await session.delete(faq)
        await session.commit()
    return HTMLResponse("")
