"""Content the bot answers with: FAQ, Knowledge Base, Intents and custom Commands."""
import re

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import FAQ, FAQ_CATEGORIES, Admin, Command, Intent, KnowledgeArticle, TrainingPhrase, utcnow
from app.services import logs
from app.services.validators import extract_entities
from app.web.deps import get_session, partial, render, require

router = APIRouter()
LANGS = {"en": "English", "km": "Khmer"}
ENTITY_KINDS = ["phone", "email", "date", "number"]
RESERVED_COMMANDS = {"start", "help", "menu", "cancel"}


def _lang(value: str) -> str:
    return value if value in LANGS else "en"


async def _get(session: AsyncSession, model, item_id: int):
    item = await session.get(model, item_id)
    if item is None:
        raise HTTPException(404, "Not found")
    return item


# ---- FAQ ---------------------------------------------------------------------
@router.get("/faq", response_class=HTMLResponse)
async def faq_page(request: Request, q: str = "", category: str = "", question: str = "",
                   admin: Admin = Depends(require("view")), session: AsyncSession = Depends(get_session)):
    query = select(FAQ).order_by(FAQ.id.desc())
    if q:
        query = query.where(FAQ.question.ilike(f"%{q}%") | FAQ.answer.ilike(f"%{q}%") | FAQ.keywords.ilike(f"%{q}%"))
    if category:
        query = query.where(FAQ.category == category)
    faqs = (await session.execute(query)).scalars().all()
    return await render(request, "faq.html", admin, session, "FAQ", faqs=faqs, categories=FAQ_CATEGORIES,
                        q=q, category=category, prefill=question)


@router.post("/faq", response_class=HTMLResponse)
async def faq_create(request: Request, question: str = Form(...), answer: str = Form(...),
                     category: str = Form("General"), keywords: str = Form(""), language: str = Form("en"),
                     priority: int = Form(0), admin: Admin = Depends(require("create")),
                     session: AsyncSession = Depends(get_session)):
    """HTMX: add a FAQ and return only the new table row."""
    faq = FAQ(question=question.strip(), answer=answer.strip(), category=category, keywords=keywords.strip(),
              language=_lang(language), priority=priority)
    session.add(faq)
    await session.commit()
    await logs.audit(session, admin.email, "Created FAQ", faq.id, faq.question)
    return partial(request, "_faq_row.html", admin, f=faq)


@router.post("/faq/{faq_id}/toggle", response_class=HTMLResponse)
async def faq_toggle(request: Request, faq_id: int, admin: Admin = Depends(require("edit")),
                     session: AsyncSession = Depends(get_session)):
    faq = await _get(session, FAQ, faq_id)
    faq.status = "Inactive" if faq.status == "Active" else "Active"
    await logs.audit(session, admin.email, f"FAQ {faq.status}", faq.id)
    return partial(request, "_faq_row.html", admin, f=faq)


@router.delete("/faq/{faq_id}", response_class=HTMLResponse)
async def faq_delete(faq_id: int, admin: Admin = Depends(require("delete")),
                     session: AsyncSession = Depends(get_session)):
    faq = await session.get(FAQ, faq_id)
    if faq:
        await session.delete(faq)
        await logs.audit(session, admin.email, "Deleted FAQ", faq_id, faq.question)
    return HTMLResponse("")


# ---- Knowledge Base ----------------------------------------------------------
@router.get("/knowledge", response_class=HTMLResponse)
async def knowledge_page(request: Request, q: str = "", admin: Admin = Depends(require("view")),
                         session: AsyncSession = Depends(get_session)):
    query = select(KnowledgeArticle).order_by(KnowledgeArticle.updated_at.desc())
    if q:
        like = f"%{q}%"
        query = query.where(KnowledgeArticle.title.ilike(like) | KnowledgeArticle.content.ilike(like)
                            | KnowledgeArticle.keywords.ilike(like))
    articles = (await session.execute(query)).scalars().all()
    return await render(request, "knowledge.html", admin, session, "Knowledge Base", articles=articles,
                        categories=FAQ_CATEGORIES, q=q)


@router.post("/knowledge", response_class=HTMLResponse)
async def knowledge_create(request: Request, title: str = Form(...), content: str = Form(...),
                           category: str = Form("General"), keywords: str = Form(""), language: str = Form("en"),
                           status: str = Form("Published"), admin: Admin = Depends(require("create")),
                           session: AsyncSession = Depends(get_session)):
    article = KnowledgeArticle(title=title.strip(), content=content.strip(), category=category,
                               keywords=keywords.strip(), language=_lang(language), author_id=admin.id,
                               status=status if status in ("Published", "Draft") else "Draft")
    session.add(article)
    await session.commit()
    await logs.audit(session, admin.email, "Created article", article.id, article.title)
    return partial(request, "_article_row.html", admin, a=article)


@router.post("/knowledge/{article_id}/toggle", response_class=HTMLResponse)
async def knowledge_toggle(request: Request, article_id: int, admin: Admin = Depends(require("edit")),
                           session: AsyncSession = Depends(get_session)):
    article = await _get(session, KnowledgeArticle, article_id)
    article.status = "Draft" if article.status == "Published" else "Published"
    article.updated_at = utcnow()
    await logs.audit(session, admin.email, f"Article {article.status}", article.id)
    return partial(request, "_article_row.html", admin, a=article)


@router.delete("/knowledge/{article_id}", response_class=HTMLResponse)
async def knowledge_delete(article_id: int, admin: Admin = Depends(require("delete")),
                           session: AsyncSession = Depends(get_session)):
    article = await session.get(KnowledgeArticle, article_id)
    if article:
        await session.delete(article)
        await logs.audit(session, admin.email, "Deleted article", article_id, article.title)
    return HTMLResponse("")


# ---- Intents -----------------------------------------------------------------
def parse_phrases(text: str) -> list[tuple[str, str]]:
    """One training phrase per line. 'km: ...' marks a Khmer phrase; Khmer letters are detected too."""
    phrases = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = re.match(r"^(en|km)\s*:\s*(.+)$", line)
        if match:
            phrases.append((match.group(2).strip(), match.group(1)))
        else:
            khmer = any("ក" <= ch <= "៿" for ch in line)
            phrases.append((line, "km" if khmer else "en"))
    return phrases


async def _intent(session: AsyncSession, intent_id: int) -> Intent:
    intent = (await session.execute(
        select(Intent).where(Intent.id == intent_id).options(selectinload(Intent.phrases))
    )).scalar_one_or_none()
    if intent is None:
        raise HTTPException(404, "Intent not found")
    return intent


@router.get("/intents", response_class=HTMLResponse)
async def intents_page(request: Request, admin: Admin = Depends(require("view")),
                       session: AsyncSession = Depends(get_session)):
    intents = (await session.execute(
        select(Intent).order_by(Intent.priority.desc(), Intent.name).options(selectinload(Intent.phrases))
    )).scalars().all()
    return await render(request, "intents.html", admin, session, "Intents", intents=intents,
                        entity_kinds=ENTITY_KINDS)


@router.post("/intents", response_class=HTMLResponse)
async def intent_create(request: Request, name: str = Form(...), description: str = Form(""),
                        response: str = Form(""), phrases: str = Form(...), priority: int = Form(0),
                        admin: Admin = Depends(require("train")), session: AsyncSession = Depends(get_session)):
    form = await request.form()
    entities = [kind for kind in form.getlist("entities") if kind in ENTITY_KINDS]
    name = re.sub(r"[^a-z0-9_]+", "_", name.strip().lower()).strip("_")
    if not name:
        raise HTTPException(400, "The intent name is empty")
    if (await session.execute(select(Intent).where(Intent.name == name))).scalar_one_or_none():
        raise HTTPException(400, f"An intent named {name} already exists")
    intent = Intent(name=name, description=description.strip(), response=response.strip(), entities=entities,
                    priority=priority,
                    phrases=[TrainingPhrase(phrase=p, language=lang) for p, lang in parse_phrases(phrases)])
    session.add(intent)
    await session.commit()
    await logs.audit(session, admin.email, "Created intent", intent.id, name)
    return partial(request, "_intent_row.html", admin, i=await _intent(session, intent.id))


@router.post("/intents/{intent_id}/phrases", response_class=HTMLResponse)
async def intent_add_phrases(request: Request, intent_id: int, phrases: str = Form(...),
                             admin: Admin = Depends(require("train")), session: AsyncSession = Depends(get_session)):
    intent = await _intent(session, intent_id)
    for phrase, lang in parse_phrases(phrases):
        intent.phrases.append(TrainingPhrase(phrase=phrase, language=lang))
    await logs.audit(session, admin.email, "Added training phrases", intent.id, phrases)
    return partial(request, "_intent_row.html", admin, i=await _intent(session, intent_id))


@router.post("/intents/{intent_id}/toggle", response_class=HTMLResponse)
async def intent_toggle(request: Request, intent_id: int, admin: Admin = Depends(require("train")),
                        session: AsyncSession = Depends(get_session)):
    intent = await _intent(session, intent_id)
    intent.status = "Inactive" if intent.status == "Active" else "Active"
    await logs.audit(session, admin.email, f"Intent {intent.status}", intent.id)
    return partial(request, "_intent_row.html", admin, i=intent)


@router.delete("/intents/{intent_id}", response_class=HTMLResponse)
async def intent_delete(intent_id: int, admin: Admin = Depends(require("delete")),
                        session: AsyncSession = Depends(get_session)):
    intent = await _intent(session, intent_id)
    for phrase in intent.phrases:
        await session.delete(phrase)
    await session.delete(intent)
    await logs.audit(session, admin.email, "Deleted intent", intent_id, intent.name)
    return HTMLResponse("")


@router.post("/intents/test", response_class=HTMLResponse)
async def intent_test(request: Request, text: str = Form(...), language: str = Form("en"),
                      admin: Admin = Depends(require("view")), session: AsyncSession = Depends(get_session)):
    """Try a sentence and see which intent and entities the bot detects."""
    from app.services.intents import detect_intent

    match = await detect_intent(session, text, _lang(language))
    return partial(request, "_intent_test.html", admin, match=match, text=text,
                   all_entities=extract_entities(text))


# ---- Commands ----------------------------------------------------------------
@router.get("/commands", response_class=HTMLResponse)
async def commands_page(request: Request, admin: Admin = Depends(require("view")),
                        session: AsyncSession = Depends(get_session)):
    commands = (await session.execute(select(Command).order_by(Command.name))).scalars().all()
    return await render(request, "commands.html", admin, session, "Commands", commands=commands,
                        reserved=sorted(RESERVED_COMMANDS))


@router.post("/commands", response_class=HTMLResponse)
async def command_create(request: Request, name: str = Form(...), description: str = Form(""),
                         response: str = Form(...), admin: Admin = Depends(require("create")),
                         session: AsyncSession = Depends(get_session)):
    name = name.strip().lstrip("/").lower()
    if not re.fullmatch(r"[a-z0-9_]{1,32}", name) or name in RESERVED_COMMANDS:
        raise HTTPException(400, "Use 1-32 lowercase letters, digits or _ (and not a built-in command)")
    if (await session.execute(select(Command).where(Command.name == name))).scalar_one_or_none():
        raise HTTPException(400, f"/{name} already exists")
    command = Command(name=name, description=description.strip(), response=response.strip())
    session.add(command)
    await session.commit()
    await logs.audit(session, admin.email, "Created command", command.id, f"/{name}")
    return partial(request, "_command_row.html", admin, cmd=command)


@router.post("/commands/{command_id}/toggle", response_class=HTMLResponse)
async def command_toggle(request: Request, command_id: int, admin: Admin = Depends(require("edit")),
                         session: AsyncSession = Depends(get_session)):
    command = await _get(session, Command, command_id)
    command.status = "Inactive" if command.status == "Active" else "Active"
    await logs.audit(session, admin.email, f"Command {command.status}", command.id)
    return partial(request, "_command_row.html", admin, cmd=command)


@router.delete("/commands/{command_id}", response_class=HTMLResponse)
async def command_delete(command_id: int, admin: Admin = Depends(require("delete")),
                         session: AsyncSession = Depends(get_session)):
    command = await session.get(Command, command_id)
    if command:
        await session.delete(command)
        await logs.audit(session, admin.email, "Deleted command", command_id, f"/{command.name}")
    return HTMLResponse("")
