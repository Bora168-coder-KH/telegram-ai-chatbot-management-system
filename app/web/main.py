"""Admin dashboard (FastAPI + Jinja2 + HTMX).

Run:  uvicorn app.web.main:app --reload
Open: http://127.0.0.1:8000  (log in with ADMIN_EMAIL / ADMIN_PASSWORD from .env)
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.db import SessionLocal, init_db
from app.seed import seed_defaults
from app.services.masking import mask_text, pii
from app.web.deps import BASE_DIR, LoginRequired, templates
from app.web.routes import auth, broadcast, content, conversations, dashboard, reports
from app.web.routes import settings as settings_routes
from app.web import webhook
from app.web.timeutil import localtime


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with SessionLocal() as session:
        await seed_defaults(session)
    if webhook.enabled():
        await webhook.start()
    yield
    if webhook.enabled():
        await webhook.stop()


app = FastAPI(title="AI Chatbot Management System", lifespan=lifespan)
app.add_middleware(
    SessionMiddleware, secret_key=settings.secret_key, session_cookie="chatbot_admin",
    max_age=12 * 3600, same_site="lax", https_only=settings.secure_cookies,
)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates.env.filters["pii"] = pii
templates.env.filters["pii_text"] = mask_text
templates.env.filters["localtime"] = localtime

for module in (auth, dashboard, conversations, content, broadcast, reports, settings_routes, webhook):
    app.include_router(module.router)


@app.exception_handler(LoginRequired)
async def login_required(request: Request, exc: LoginRequired):
    url = f"/login?next={exc.next_url}"
    if request.headers.get("hx-request"):
        return HTMLResponse("", headers={"HX-Redirect": url})
    return RedirectResponse(url, status_code=303)


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    if request.headers.get("hx-request"):  # shown in the page's error banner by base.html
        return HTMLResponse(str(exc.detail), status_code=exc.status_code)
    return templates.TemplateResponse(request, "error.html", {"status": exc.status_code, "detail": exc.detail},
                                      status_code=exc.status_code)


@app.get("/")
async def index():
    return RedirectResponse("/dashboard")


@app.get("/health")
async def health():
    return {"status": "ok"}
