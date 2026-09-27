# Telegram AI Chatbot Management System

A hybrid Telegram chatbot (Khmer and English) with an admin dashboard.
Users ask questions in Telegram; the bot answers with **commands, keyword rules, FAQ, Knowledge Base and AI**,
falls back politely when it cannot answer, and can hand the conversation to a human agent.
Admins manage everything from a web dashboard.

```
User Message -> Command -> Keyword / Rule -> FAQ -> Knowledge Base -> AI -> Fallback -> Human Handoff
```

**Tech stack:** Python 3.11+, aiogram (bot), FastAPI + Jinja2 + HTMX (admin dashboard),
SQLAlchemy 2.0 (async) with SQLite in development and PostgreSQL later, pytest.

## What already works (starter)

- Bot: `/start` (registers the user, language choice, Main Menu), `/help`, `/menu`, custom commands from the database
- Reply Keyboard main menu, Inline Keyboards, Callback Query (language, FAQ list, feedback, fallback buttons)
- Response routing: rule -> FAQ (exact, similar, keyword) -> Knowledge Base -> AI hook -> fallback
- Unknown question detection (saved with a counter for admin review)
- Every incoming and outgoing message is stored with its response source
- Image, document, voice (prototype) and location messages are stored; unsupported types get a clear reply
- Feedback with thumbs up / down and 1-5 stars
- Blocked / suspended users and Maintenance Mode are respected
- Human support request (conversation marked as an open support request)
- Dashboard: statistic cards and KPIs, Users (search, change status with HTMX), FAQ (add and delete with HTMX)
- 16 data models from the ERD (plus `UnknownQuestion`)

See [`docs/roadmap.md`](docs/roadmap.md) for everything that is still to do, split by teammate.

## Quick start

```bash
# 1. Create a virtual environment and install packages
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure secrets
cp .env.example .env                 # Windows: copy .env.example .env
# open .env and paste your BOT_TOKEN from @BotFather

# 3. Run the bot (Long Polling)
python -m app.bot.main

# 4. In a second terminal, run the admin dashboard
uvicorn app.web.main:app --reload
# open http://127.0.0.1:8000
```

The first run creates `chatbot.db` (SQLite) and adds sample FAQs, one Knowledge Base article and the five roles.
Then open your bot in Telegram and send `/start`.

Run the tests: `pytest`

> **Never commit `.env`.** The Bot Token and API keys must stay out of GitHub (`.env` is in `.gitignore`).
> If a token is ever pushed by mistake, revoke it in @BotFather and create a new one.

## Project structure

```
app/
  config.py            settings from .env
  db.py                async engine and session
  models.py            data models (ERD)
  i18n.py              Khmer / English texts
  seed.py              sample data (python -m app.seed)
  bot/
    main.py            starts the bot (Long Polling), verifies the token
    handlers.py        commands, menu buttons, callbacks, messages
    keyboards.py       Reply and Inline keyboards
    middlewares.py     database session for every handler
  services/
    router.py          Response Routing Logic
    rules.py           keyword / rule responses
    ai.py              AI hook (to implement)
    users.py           users, conversations, messages
    stats.py           dashboard statistics and KPIs
  web/
    main.py            FastAPI routes
    templates/         Jinja2 + HTMX pages
    static/style.css
tests/                 pytest tests
docs/                  architecture and roadmap
```

## How the routing works

`app/services/router.py` tries each source in order and stops at the first answer:

1. **Keyword / rule** - simple word matches in `services/rules.py`
2. **FAQ** - similar question (difflib) or a keyword found in the message
3. **Knowledge Base** - article keywords; the article text is used as AI context when AI is enabled
4. **AI** - `services/ai.py` (returns nothing until you connect a provider)
5. **Fallback** - polite message, the question is saved as an unknown question, buttons offer Rephrase / Main Menu / Human Support

## Suggested git workflow for the team

- `main` is always working. Work in branches: `feature/intents`, `feature/broadcast`, `docs/testing`.
- Small commits with clear messages, then a pull request that at least one teammate reviews.
- Run `pytest` before opening a pull request.

## Team

Group 1 - Ponloeng Bora, Phal Raksa, Tan Mengkoung, Lay Sopanha.
