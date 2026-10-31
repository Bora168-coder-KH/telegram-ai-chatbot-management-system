"""Broadcast page: audience, preview, send now or schedule, history."""
import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal
from app.models import Admin, Broadcast, utcnow
from app.services import broadcast as svc
from app.services import logs
from app.web.deps import get_session, partial, render, require
from app.web.timeutil import local_to_utc

router = APIRouter()
_tasks: set[asyncio.Task] = set()  # keep a reference so "send now" tasks are not garbage-collected


async def _send_in_background(broadcast_id: int) -> None:
    try:
        async with SessionLocal() as session:
            broadcast = await session.get(Broadcast, broadcast_id)
            if broadcast:
                await svc.send(session, broadcast)
    except Exception as exc:
        await logs.error("broadcast send", exc, details=f"broadcast {broadcast_id}")


async def _history(session: AsyncSession) -> list[Broadcast]:
    return list((await session.execute(select(Broadcast).order_by(Broadcast.id.desc()).limit(50))).scalars())


@router.get("/broadcast", response_class=HTMLResponse)
async def broadcast_page(request: Request, admin: Admin = Depends(require("broadcast")),
                         session: AsyncSession = Depends(get_session)):
    return await render(request, "broadcast.html", admin, session, "Broadcast",
                        audiences=svc.AUDIENCES, history=await _history(session))


@router.post("/broadcast/preview", response_class=HTMLResponse)
async def broadcast_preview(request: Request, message: str = Form(""), audience: str = Form("all"),
                            user_ids: str = Form(""), admin: Admin = Depends(require("broadcast")),
                            session: AsyncSession = Depends(get_session)):
    """HTMX: how the message will look, and who will receive it."""
    users = await svc.recipients(session, audience, svc.parse_ids(user_ids))
    return partial(request, "_broadcast_preview.html", admin, message=message, users=users,
                   audience=svc.AUDIENCES.get(audience, audience))


@router.post("/broadcast", response_class=HTMLResponse)
async def broadcast_create(request: Request, message: str = Form(...), audience: str = Form("all"),
                           user_ids: str = Form(""), scheduled_at: str = Form(""),
                           admin: Admin = Depends(require("broadcast")), session: AsyncSession = Depends(get_session)):
    when = None
    if scheduled_at:
        try:
            when = local_to_utc(datetime.fromisoformat(scheduled_at))
        except ValueError:
            raise HTTPException(400, "The schedule time is not valid")
        if when <= utcnow():
            raise HTTPException(400, "The schedule time is in the past")
    try:
        item = await svc.create(session, message, audience, svc.parse_ids(user_ids), when, admin.id)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    await logs.audit(session, admin.email, "Scheduled broadcast" if when else "Sent broadcast", item.id,
                     f"{audience}: {item.message[:100]}")
    if not when:
        task = asyncio.create_task(_send_in_background(item.id))
        _tasks.add(task)
        task.add_done_callback(_tasks.discard)
    return partial(request, "_broadcast_history.html", admin, history=await _history(session))


@router.get("/broadcast/history", response_class=HTMLResponse)
async def broadcast_history(request: Request, admin: Admin = Depends(require("broadcast")),
                            session: AsyncSession = Depends(get_session)):
    return partial(request, "_broadcast_history.html", admin, history=await _history(session))


@router.post("/broadcast/{broadcast_id}/cancel", response_class=HTMLResponse)
async def broadcast_cancel(request: Request, broadcast_id: int, admin: Admin = Depends(require("broadcast")),
                           session: AsyncSession = Depends(get_session)):
    item = await session.get(Broadcast, broadcast_id)
    if item and item.status == "scheduled":
        item.status = "cancelled"
        await logs.audit(session, admin.email, "Cancelled broadcast", item.id)
    return partial(request, "_broadcast_history.html", admin, history=await _history(session))
