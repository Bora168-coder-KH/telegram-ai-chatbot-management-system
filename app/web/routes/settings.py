"""Settings: bot info, AI settings, System Prompt, maintenance mode, roles and admin accounts. Also Logs."""
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Admin, Agent, Bot, Log, Role
from app.services import logs
from app.services.ai import STYLES, ai_enabled
from app.services.auth import PERMISSIONS, hash_password, verify_password
from app.web.deps import current_admin, get_session, render, require

router = APIRouter()
ADMIN_ROLE = "Administrator"


def require_administrator(admin: Admin = Depends(require("edit"))) -> Admin:
    if admin.role.name != ADMIN_ROLE:
        raise HTTPException(403, "Only an Administrator can manage roles and accounts.")
    return admin


async def _bot(session: AsyncSession) -> Bot:
    bot = (await session.execute(select(Bot))).scalars().first()
    if bot is None:
        bot = Bot()
        session.add(bot)
        await session.commit()
    return bot


def _back(message: str, request: Request, anchor: str = "") -> RedirectResponse:
    request.session["flash"] = message
    return RedirectResponse(f"/settings{anchor}", status_code=303)


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, admin: Admin = Depends(require("edit")),
                        session: AsyncSession = Depends(get_session)):
    roles = (await session.execute(select(Role).order_by(Role.id))).scalars().all()
    admins = (await session.execute(select(Admin).order_by(Admin.id).options(selectinload(Admin.role)))).scalars().all()
    agents = {a.admin_id: a for a in (await session.execute(select(Agent))).scalars()}
    return await render(request, "settings.html", admin, session, "Settings", bot=await _bot(session),
                        styles=STYLES, ai_ready=ai_enabled(), roles=roles, admins=admins, agents=agents,
                        permissions=PERMISSIONS, is_administrator=admin.role.name == ADMIN_ROLE)


@router.post("/settings/bot")
async def save_bot(request: Request, name: str = Form(...), username: str = Form(""),
                   default_language: str = Form("en"), welcome_message: str = Form(""),
                   fallback_message: str = Form(""), support_contact: str = Form(""),
                   maintenance_mode: str = Form(""), admin: Admin = Depends(require("edit")),
                   session: AsyncSession = Depends(get_session)):
    bot = await _bot(session)
    bot.name, bot.username = name.strip(), username.strip().lstrip("@")
    bot.default_language = default_language if default_language in ("en", "km") else "en"
    bot.welcome_message, bot.fallback_message = welcome_message.strip(), fallback_message.strip()
    bot.support_contact = support_contact.strip()
    bot.maintenance_mode = maintenance_mode == "on"
    await logs.audit(session, admin.email, "Updated bot settings", bot.id,
                     f"maintenance={'on' if bot.maintenance_mode else 'off'}")
    return _back("Bot settings saved.", request, "#bot")


@router.post("/settings/ai")
async def save_ai(request: Request, ai_model: str = Form(""), ai_temperature: float = Form(0.3),
                  ai_max_length: int = Form(500), response_style: str = Form("short"),
                  system_prompt: str = Form(""), admin: Admin = Depends(require("train")),
                  session: AsyncSession = Depends(get_session)):
    bot = await _bot(session)
    bot.ai_model = ai_model.strip()
    bot.ai_temperature = min(max(ai_temperature, 0.0), 2.0)
    bot.ai_max_length = min(max(ai_max_length, 50), 4000)
    bot.response_style = response_style if response_style in STYLES else "short"
    bot.system_prompt = system_prompt.strip()
    await logs.audit(session, admin.email, "Updated AI settings", bot.id)
    return _back("AI settings saved.", request, "#ai")


@router.post("/settings/roles/{role_id}")
async def save_role(request: Request, role_id: int, admin: Admin = Depends(require_administrator),
                    session: AsyncSession = Depends(get_session)):
    role = await session.get(Role, role_id)
    if role is None:
        raise HTTPException(404, "Role not found")
    if role.name == ADMIN_ROLE:
        return _back("The Administrator role always has every permission.", request, "#roles")
    form = await request.form()
    role.permissions = [p for p in PERMISSIONS if p in form.getlist("permissions")]
    await logs.audit(session, admin.email, "Changed role permissions", role.id, f"{role.name}: {role.permissions}")
    return _back(f"Permissions for {role.name} saved.", request, "#roles")


@router.post("/settings/admins")
async def create_admin(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...),
                       role_id: int = Form(...), is_agent: str = Form(""),
                       admin: Admin = Depends(require_administrator), session: AsyncSession = Depends(get_session)):
    email = email.strip().lower()
    if len(password) < 8:
        return _back("The password must have at least 8 characters.", request, "#admins")
    if (await session.execute(select(Admin).where(Admin.email == email))).scalar_one_or_none():
        return _back(f"{email} already has an account.", request, "#admins")
    if await session.get(Role, role_id) is None:
        raise HTTPException(400, "Unknown role")
    new = Admin(name=name.strip(), email=email, password_hash=hash_password(password), role_id=role_id)
    session.add(new)
    await session.flush()
    if is_agent == "on":
        session.add(Agent(admin_id=new.id))
    await logs.audit(session, admin.email, "Created admin account", new.id, email)
    return _back(f"Account {email} created.", request, "#admins")


@router.post("/settings/admins/{admin_id}")
async def update_admin(request: Request, admin_id: int, role_id: int = Form(...), status: str = Form("Active"),
                       is_agent: str = Form(""), availability: str = Form("available"),
                       admin: Admin = Depends(require_administrator), session: AsyncSession = Depends(get_session)):
    target = await session.get(Admin, admin_id)
    if target is None:
        raise HTTPException(404, "Account not found")
    if target.id == admin.id and (status != "Active" or role_id != target.role_id):
        return _back("You cannot disable or change the role of your own account.", request, "#admins")
    target.role_id, target.status = role_id, status if status in ("Active", "Disabled") else "Active"
    agent = (await session.execute(select(Agent).where(Agent.admin_id == target.id))).scalar_one_or_none()
    availability = availability if availability in ("available", "away") else "available"
    if is_agent == "on" and agent is None:
        session.add(Agent(admin_id=target.id, availability=availability))
    elif is_agent == "on" and agent:
        agent.availability = availability
    elif is_agent != "on" and agent:
        agent.availability = "off"  # no longer an agent; the row stays because old conversations point to it
    await logs.audit(session, admin.email, "Updated admin account", target.id,
                     f"role={role_id} status={target.status} agent={is_agent == 'on'}")
    return _back(f"Account {target.email} saved.", request, "#admins")


@router.post("/settings/password")
async def change_password(request: Request, current: str = Form(...), new: str = Form(...),
                          admin: Admin = Depends(current_admin), session: AsyncSession = Depends(get_session)):
    if not verify_password(current, admin.password_hash):
        return _back("Your current password is wrong.", request, "#password")
    if len(new) < 8:
        return _back("The new password must have at least 8 characters.", request, "#password")
    admin.password_hash = hash_password(new)
    await logs.audit(session, admin.email, "Changed own password", admin.id)
    return _back("Password changed.", request, "#password")


@router.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request, type: str = "", q: str = "", admin: Admin = Depends(require("report")),
                    session: AsyncSession = Depends(get_session)):
    query = select(Log).order_by(Log.id.desc()).limit(300)
    if type:
        query = query.where(Log.log_type == type)
    if q:
        like = f"%{q}%"
        query = query.where(Log.action.ilike(like) | Log.actor.ilike(like) | Log.details.ilike(like))
    rows = (await session.execute(query)).scalars().all()
    return await render(request, "logs.html", admin, session, "Logs", rows=rows, type=type, q=q,
                        types=["Activity", "Audit", "Conversation", "Error"])
