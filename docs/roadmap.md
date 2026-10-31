# Roadmap

Legend: [x] done in the starter, [ ] to do. Owners follow the Work Distribution in Notion.
Everyone can pick up any task; the owner is the person who makes sure it gets finished.

## Tan Mengkoung - design, data, integration, security
- [x] Data models for the ERD (`app/models.py`)
- [x] Bot authentication (token check on start)
- [x] Long Polling
- [x] Webhook mode (FastAPI endpoint + `set_webhook`) for the final demo
- [x] Alembic migrations (replace `create_all`)
- [ ] Switch to PostgreSQL (`docker-compose.yml` is ready). Code, asyncpg and `scripts/copy_database.py` are ready and tested on SQLite; still to do: run it once against a real PostgreSQL server (see README)
- [x] AI provider integration in `services/ai.py` (prompt, timeout, retry, error handling)
- [x] Retry logic for Telegram API errors
- [x] Error Log, Activity Log and Audit Log writing (`Log` model)
- [x] Data masking for Telegram user data by role
- [x] Backup and recovery script (prototype)

## Phal Raksa - features, requirements, business logic, testing
- [x] `/start`, `/help`, `/menu`, custom commands
- [x] Response routing (rule, FAQ, Knowledge Base, AI hook, fallback)
- [x] Unknown question detection
- [x] Feedback (thumbs and stars)
- [x] Intent detection with training phrases and entity extraction
- [x] Form conversation (Name -> Phone -> Email -> Request -> Confirmation) using `Conversation.session_step` and `context`
- [x] Input validation (phone, email, date, number) and invalid input handling
- [x] Human handoff: assign agent, agent queue, status changes (Open, Assigned, In Progress, Resolved, Closed)
- [x] Notifications (welcome, reminder, support reply) and scheduled broadcast (APScheduler)
- [x] Rate limit, spam detection, content moderation (prototypes)
- [x] Admin login, session, auto logout, role and permission checks
- [x] More tests: intents, forms, handoff, permissions, end-to-end

## Lay Sopanha - UI/UX, documentation, demo
- [x] Bot main menu (Reply Keyboard) and inline keyboards
- [x] Dashboard, Users and FAQ pages (starter)
- [x] Conversations page: history timeline, agent reply box
- [x] Knowledge Base, Intents and Commands pages
- [x] Broadcast page (audience, preview, schedule, history)
- [x] Reports page with export to PDF and Excel
- [x] Settings page (bot info, AI settings, System Prompt, maintenance mode, roles)
- [x] Charts on the dashboard (Chart.js): user growth, incoming vs outgoing, popular questions
- [x] Responsive check on tablet and mobile
- [x] Screenshots, final documentation, live demo script

## Ponloeng Bora - analysis, KPIs, presentation
- [x] KPI calculations on the dashboard (resolution, AI answer, fallback, handoff, satisfaction)
- [x] Review that every requirement in the assignment is covered: `docs/requirements-coverage.md` (the Notion coverage map was not found; compare with the official brief)
- [x] Decide the exact meaning of "Resolved" for the Resolution Rate and adjust `services/stats.py`
- [x] Collect Khmer and English test questions: `docs/evaluation/test_questions.csv` (team-written; add real user questions after the demo)
- [x] Final presentation and demo storyline: `docs/demo-script.md`

## Suggested order
1. Everyone: run the starter, send `/start`, open the dashboard, read `router.py`.
2. Add Knowledge Base and Intents pages + intent detection.
3. Human handoff end to end (bot -> queue -> agent reply -> user).
4. Broadcast and notifications.
5. Reports and charts.
6. Login, roles, logs, masking.
7. Webhook, PostgreSQL, testing, documentation, demo rehearsal.
