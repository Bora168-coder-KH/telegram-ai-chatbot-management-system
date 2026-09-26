# Roadmap

Legend: [x] done in the starter, [ ] to do. Owners follow the Work Distribution in Notion.
Everyone can pick up any task; the owner is the person who makes sure it gets finished.

## Tan Mengkoung - design, data, integration, security
- [x] Data models for the ERD (`app/models.py`)
- [x] Bot authentication (token check on start)
- [x] Long Polling
- [ ] Webhook mode (FastAPI endpoint + `set_webhook`) for the final demo
- [ ] Alembic migrations (replace `create_all`)
- [ ] Switch to PostgreSQL (`docker-compose.yml` is ready)
- [ ] AI provider integration in `services/ai.py` (prompt, timeout, retry, error handling)
- [ ] Retry logic for Telegram API errors
- [ ] Error Log, Activity Log and Audit Log writing (`Log` model)
- [ ] Data masking for Telegram user data by role
- [ ] Backup and recovery script (prototype)

## Phal Raksa - features, requirements, business logic, testing
- [x] `/start`, `/help`, `/menu`, custom commands
- [x] Response routing (rule, FAQ, Knowledge Base, AI hook, fallback)
- [x] Unknown question detection
- [x] Feedback (thumbs and stars)
- [ ] Intent detection with training phrases and entity extraction
- [ ] Form conversation (Name -> Phone -> Email -> Request -> Confirmation) using `Conversation.session_step` and `context`
- [ ] Input validation (phone, email, date, number) and invalid input handling
- [ ] Human handoff: assign agent, agent queue, status changes (Open, Assigned, In Progress, Resolved, Closed)
- [ ] Notifications (welcome, reminder, support reply) and scheduled broadcast (APScheduler)
- [ ] Rate limit, spam detection, content moderation (prototypes)
- [ ] Admin login, session, auto logout, role and permission checks
- [ ] More tests: intents, forms, handoff, permissions, end-to-end

## Lay Sopanha - UI/UX, documentation, demo
- [x] Bot main menu (Reply Keyboard) and inline keyboards
- [x] Dashboard, Users and FAQ pages (starter)
- [ ] Conversations page: history timeline, agent reply box
- [ ] Knowledge Base, Intents and Commands pages
- [ ] Broadcast page (audience, preview, schedule, history)
- [ ] Reports page with export to PDF and Excel
- [ ] Settings page (bot info, AI settings, System Prompt, maintenance mode, roles)
- [ ] Charts on the dashboard (Chart.js): user growth, incoming vs outgoing, popular questions
- [ ] Responsive check on tablet and mobile
- [ ] Screenshots, final documentation, live demo script

## Ponloeng Bora - analysis, KPIs, presentation
- [x] KPI calculations on the dashboard (resolution, AI answer, fallback, handoff, satisfaction)
- [ ] Review that every requirement in the assignment is covered (use the coverage map in Notion)
- [ ] Decide the exact meaning of "Resolved" for the Resolution Rate and adjust `services/stats.py`
- [ ] Collect real Khmer and English test questions for the FAQ and Knowledge Base
- [ ] Final presentation and demo storyline

## Suggested order
1. Everyone: run the starter, send `/start`, open the dashboard, read `router.py`.
2. Add Knowledge Base and Intents pages + intent detection.
3. Human handoff end to end (bot -> queue -> agent reply -> user).
4. Broadcast and notifications.
5. Reports and charts.
6. Login, roles, logs, masking.
7. Webhook, PostgreSQL, testing, documentation, demo rehearsal.
