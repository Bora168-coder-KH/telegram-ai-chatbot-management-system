# Telegram AI Chatbot Management System

A hybrid Telegram chatbot (Khmer and English) with an admin dashboard.
Users ask questions in Telegram; the bot answers with **commands, keyword rules, intents, FAQ, Knowledge Base and AI**,
falls back politely when it cannot answer, and hands the conversation to a human agent.
Admins and agents manage everything from a web dashboard.

```
User Message -> Command -> Keyword / Rule -> Intent -> FAQ -> Knowledge Base -> AI -> Fallback -> Human Handoff
```

**Tech stack:** Python 3.11+, aiogram (bot), FastAPI + Jinja2 + HTMX + Chart.js (dashboard),
SQLAlchemy 2.0 (async) with Alembic migrations, SQLite or PostgreSQL, APScheduler, pytest.

![Dashboard](docs/screenshots/dashboard.png)

## Features

**Bot (Telegram)**
- `/start` (registers the user, language choice, Main Menu), `/help`, `/menu`, `/cancel`, custom commands
- Reply Keyboard main menu, Inline Keyboards, FAQ menu by category
- Response routing: rule → intent (training phrases + phone/email/date/number entities) → FAQ (similar question or
  keyword) → Knowledge Base → AI → fallback with Rephrase / Main Menu / Human Support buttons
- Contact form: Name → Phone → Email → Request → Confirmation, with validation (Cambodian phone formats, Khmer digits)
- Human handoff: requests are auto-assigned to the least busy available agent; while an agent handles a
  conversation the bot only stores the user's messages
- Feedback (👍 / 👎 and 1-5 stars), notifications (welcome, form reminder, support reply, status update)
- Rate limit, spam detection (auto-suspend after repeated spam), blocked words
- Image, document, voice and location messages are stored; blocked / suspended users and maintenance mode respected
- Retry on Telegram flood limits, network and server errors

**Dashboard**
- Login with roles (Administrator, Bot Manager, Content Manager, Support Agent, Viewer), auto logout, CSRF protection
- Dashboard: statistics, KPIs (Resolution Rate, Bot Answer Rate, AI Answer Rate, Fallback Rate, Handoff Rate,
  Satisfaction), charts, top unanswered questions → Add FAQ
- Users (search, status), Conversations (agent queue, live timeline, assign, status, reply in Telegram),
  FAQ, Knowledge Base, Intents (with a sentence tester), Commands, Broadcast (audience, live preview, schedule,
  history), Reports (date range, Excel and PDF export with Khmer text), Settings (bot info, maintenance mode,
  AI settings and System Prompt, roles, accounts and agents), Logs (Activity, Conversation, Audit, Error)
- Personal data is masked for roles without the `reply` permission

Screenshots of every page are in [`docs/screenshots/`](docs/screenshots).

## Quick start

```bash
# 1. Create a virtual environment and install packages
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure secrets
cp .env.example .env                 # Windows: copy .env.example .env
# open .env: paste BOT_TOKEN from @BotFather, set SECRET_KEY and ADMIN_PASSWORD

# 3. Run the bot (Long Polling + scheduler)
python -m app.bot.main

# 4. In a second terminal, run the admin dashboard
uvicorn app.web.main:app --reload
# open http://127.0.0.1:8000 and log in with ADMIN_EMAIL / ADMIN_PASSWORD

# Optional: 140 bilingual sample FAQs
python -m app.mock_data
```

The first run creates `chatbot.db` (SQLite), applies the migrations and adds sample FAQs, intents, one Knowledge
Base article, the five roles and the first admin account (who is also a support agent). If `ADMIN_PASSWORD` is
empty, a random password is written to `admin-password.txt`; delete that file after you log in.

Run the tests: `pytest`

> **Never commit `.env`.** The Bot Token and API keys must stay out of GitHub (`.env` is in `.gitignore`).
> If a token is ever pushed by mistake, revoke it in @BotFather and create a new one.

## Configuration (`.env`)

| Setting | Meaning |
|---|---|
| `BOT_TOKEN` | Telegram bot token |
| `BOT_MODE` | `polling` (default) or `webhook` |
| `WEBHOOK_URL`, `WEBHOOK_SECRET` | public HTTPS address of the dashboard and a long random secret (webhook mode) |
| `DATABASE_URL` | `sqlite+aiosqlite:///./chatbot.db` or `postgresql+asyncpg://user:pass@host:5432/db` |
| `SECRET_KEY` | signs the dashboard session cookie; use a long random value |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD` | first admin account, created when there is none |
| `AI_API_KEY`, `AI_MODEL`, `AI_BASE_URL`, `AI_TIMEOUT` | any OpenAI-compatible chat API (OpenRouter by default); empty key = no AI |
| `DEFAULT_LANGUAGE` | `en` or `km` for new users |
| `TIMEZONE`, `SESSION_TIMEOUT_MINUTES`, `SECURE_COOKIES` | dashboard time zone, auto logout, HTTPS-only cookie |

## Webhook mode (final demo / production)

Set `BOT_MODE=webhook`, `WEBHOOK_URL=https://your-domain` and `WEBHOOK_SECRET`, then run only the dashboard:
`uvicorn app.web.main:app --host 0.0.0.0 --port 8000` behind HTTPS (for a quick demo, a tunnel such as
`cloudflared tunnel --url http://localhost:8000` gives a public HTTPS URL). The dashboard registers the webhook on
start. To go back to polling, set `BOT_MODE=polling` and start `python -m app.bot.main`; it removes the webhook.

## PostgreSQL

```bash
docker compose up -d                                   # PostgreSQL 16 from docker-compose.yml
python -m scripts.copy_database sqlite+aiosqlite:///./chatbot.db \
    postgresql+asyncpg://chatbot:chatbot@localhost:5432/chatbot
# then in .env:  DATABASE_URL=postgresql+asyncpg://chatbot:chatbot@localhost:5432/chatbot
```

The copy script migrates the empty target, copies every table and fixes the id sequences.
It has been tested SQLite → SQLite; run it once against PostgreSQL before relying on it.

## Database migrations, backup and evaluation

```bash
alembic revision --autogenerate -m "add a column"   # after changing app/models.py
alembic upgrade head                                 # also done automatically on start

python -m scripts.backup backup                      # backups/chatbot-<time>.db, keeps the newest 10
python -m scripts.backup list
python -m scripts.backup restore backups/<file>.db   # stop the bot and dashboard first

python -m scripts.evaluate_questions                 # answer quality on docs/evaluation/test_questions.csv
```

## Project structure

```
app/
  config.py            settings from .env
  db.py                async engine, session, migrations on start
  models.py            data models (ERD)
  i18n.py              Khmer / English texts
  seed.py              sample data and the first admin (python -m app.seed)
  mock_data.py         140 bilingual mock FAQs (python -m app.mock_data)
  bot/
    main.py            Long Polling entry point (+ scheduler)
    runtime.py         bot and dispatcher set-up shared with webhook mode
    handlers.py        commands, menu buttons, callbacks, forms, messages
    keyboards.py       Reply and Inline keyboards
    middlewares.py     database session; rate limit / spam / moderation
  services/
    router.py          Response Routing Logic
    rules.py           keyword / rule responses
    intents.py         intent detection and entities
    validators.py      phone, email, date, number validation
    forms.py           the contact form conversation
    handoff.py         support requests, agent queue, statuses, agent replies
    ai.py              AI provider client
    telegram.py        sending from the dashboard, retry middleware
    notifications.py   welcome, reminder, support reply, status, announcement
    broadcast.py       audience and sending
    scheduler.py       scheduled broadcasts and reminders
    stats.py           dashboard statistics, KPIs (Resolution Rate definition) and charts
    reports.py         reports, Excel and PDF export
    auth.py            password hashing and permissions
    masking.py         personal data masking by role
    moderation.py      rate limit, spam, blocked words
    logs.py            Activity, Audit, Conversation and Error logs
    users.py           users, conversations, messages
  web/
    main.py            FastAPI app, middleware, error pages
    deps.py            login, permissions, CSRF, rendering
    webhook.py         Telegram webhook endpoint
    routes/            dashboard, conversations, content, broadcast, reports, settings, auth
    templates/         Jinja2 + HTMX pages
    static/            style.css and the PDF fonts
migrations/            Alembic migrations
scripts/               backup, copy_database, evaluate_questions
tests/                 pytest tests (82)
docs/                  architecture, roadmap, requirement coverage, demo script, evaluation, screenshots
```

## Documentation

- [`docs/architecture.md`](docs/architecture.md): diagram, routing order, layers, security
- [`docs/requirements-coverage.md`](docs/requirements-coverage.md): every requirement with its code and test, KPI
  definitions, answer-quality results and open decisions
- [`docs/demo-script.md`](docs/demo-script.md): presentation storyline and live demo steps
- [`docs/roadmap.md`](docs/roadmap.md): the task list and its status

## Suggested git workflow for the team

- `main` is always working. Work in branches: `feature/intents`, `feature/broadcast`, `docs/testing`.
- Small commits with clear messages, then a pull request that at least one teammate reviews.
- Run `pytest` before opening a pull request.

## Team

Group 1 - Ponloeng Bora, Phal Raksa, Tan Mengkoung, Lay Sopanha.
