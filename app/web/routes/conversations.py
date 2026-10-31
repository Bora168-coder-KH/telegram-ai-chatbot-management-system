"""Conversations: list, history timeline, agent queue, assignment, status and agent reply."""
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Admin, Agent, Conversation, Message, SupportStatus
from app.services import handoff
from app.web.deps import get_session, partial, render, require

router = APIRouter()
FILTERS = {"queue": "Support queue", "all": "All", **{s: s for s in handoff.ALL}}


async def _load(session: AsyncSession, conversation_id: int) -> Conversation:
    conversation = (await session.execute(
        select(Conversation).where(Conversation.id == conversation_id)
        .options(selectinload(Conversation.user), selectinload(Conversation.agent).selectinload(Agent.admin))
    )).scalar_one_or_none()
    if conversation is None:
        raise HTTPException(404, "Conversation not found")
    return conversation


async def _agents(session: AsyncSession) -> list[Agent]:
    return list((await session.execute(
        select(Agent).join(Admin).where(Admin.status == "Active", Agent.availability != "off")
        .options(selectinload(Agent.admin))
    )).scalars())


async def _messages(session: AsyncSession, conversation_id: int, after: int = 0) -> list[Message]:
    return list((await session.execute(
        select(Message).where(Message.conversation_id == conversation_id, Message.id > after).order_by(Message.id)
    )).scalars())


async def _my_agent(session: AsyncSession, admin: Admin) -> Agent | None:
    return (await session.execute(select(Agent).where(Agent.admin_id == admin.id))).scalar_one_or_none()


@router.get("/conversations", response_class=HTMLResponse)
async def conversation_list(request: Request, filter: str = "queue", admin: Admin = Depends(require("view")),
                            session: AsyncSession = Depends(get_session)):
    if filter == "queue":
        rows = await handoff.queue(session)
    else:
        query = (select(Conversation).order_by(Conversation.last_message_at.desc()).limit(200)
                 .options(selectinload(Conversation.user),
                          selectinload(Conversation.agent).selectinload(Agent.admin)))
        if filter in handoff.ALL:
            query = query.where(Conversation.support_status == filter)
        rows = list((await session.execute(query)).scalars())
    return await render(request, "conversations.html", admin, session, "Conversations",
                        conversations=rows, filter=filter, filters=FILTERS)


async def _detail(request: Request, admin: Admin, session: AsyncSession, conversation: Conversation,
                  error: str = "", page: bool = True):
    context = dict(
        c=conversation, messages=await _messages(session, conversation.id), agents=await _agents(session),
        # "Assigned" is set with the Assign form, so it gets no status button
        next_statuses=sorted(handoff.TRANSITIONS.get(conversation.support_status, set()) - {SupportStatus.ASSIGNED},
                             key=handoff.ALL.index),
        error=error,
    )
    if page:
        return await render(request, "conversation.html", admin, session, "Conversations", **context)
    return partial(request, "_handoff_panel.html", admin, **context)


@router.get("/conversations/{conversation_id}", response_class=HTMLResponse)
async def conversation_detail(request: Request, conversation_id: int, admin: Admin = Depends(require("view")),
                              session: AsyncSession = Depends(get_session)):
    return await _detail(request, admin, session, await _load(session, conversation_id))


@router.get("/conversations/{conversation_id}/messages", response_class=HTMLResponse)
async def new_messages(request: Request, conversation_id: int, after: int = 0,
                       admin: Admin = Depends(require("view")), session: AsyncSession = Depends(get_session)):
    """HTMX polling: messages newer than `after`, appended to the timeline."""
    return partial(request, "_messages.html", admin, messages=await _messages(session, conversation_id, after))


@router.post("/conversations/{conversation_id}/assign", response_class=HTMLResponse)
async def assign(request: Request, conversation_id: int, agent_id: int = Form(...),
                 admin: Admin = Depends(require("reply")), session: AsyncSession = Depends(get_session)):
    conversation = await _load(session, conversation_id)
    agent = await session.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(400, "Unknown agent")
    if conversation.support_status is None:
        await handoff.request_human_support(session, conversation, auto_assign=False)
    await handoff.assign(session, conversation, agent, actor=admin.email)
    return await _detail(request, admin, session, await _load(session, conversation_id), page=False)


@router.post("/conversations/{conversation_id}/status", response_class=HTMLResponse)
async def change_status(request: Request, conversation_id: int, status: str = Form(...),
                        admin: Admin = Depends(require("reply")), session: AsyncSession = Depends(get_session)):
    conversation = await _load(session, conversation_id)
    error = ""
    try:
        await handoff.change_status(session, conversation, status, actor=admin.email)
    except ValueError as exc:
        error = str(exc)
    return await _detail(request, admin, session, await _load(session, conversation_id), error, page=False)


@router.post("/conversations/{conversation_id}/reply", response_class=HTMLResponse)
async def reply(request: Request, conversation_id: int, text: str = Form(...),
                admin: Admin = Depends(require("reply")), session: AsyncSession = Depends(get_session)):
    """Agent reply box: sends the message to the user in Telegram."""
    conversation = await _load(session, conversation_id)
    text = text.strip()
    if not text:
        return await _detail(request, admin, session, conversation, "The reply is empty.", page=False)
    result = await handoff.agent_reply(session, conversation, await _my_agent(session, admin), text, admin.email)
    error = "" if result.delivered else "Saved, but Telegram did not deliver it (see Logs)."
    response = await _detail(request, admin, session, await _load(session, conversation_id), error, page=False)
    response.headers["HX-Trigger"] = "new-message"  # the timeline fetches the new message
    return response


@router.post("/conversations/{conversation_id}/request", response_class=HTMLResponse)
async def open_request(request: Request, conversation_id: int, admin: Admin = Depends(require("reply")),
                       session: AsyncSession = Depends(get_session)):
    """Open a support request from the dashboard (e.g. after spotting a fallback)."""
    conversation = await _load(session, conversation_id)
    if conversation.support_status in (None, SupportStatus.CLOSED, SupportStatus.RESOLVED):
        await handoff.request_human_support(session, conversation, note=f"opened by {admin.email}")
    return await _detail(request, admin, session, await _load(session, conversation_id), page=False)
