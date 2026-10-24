# Requirement coverage review

Owner: Ponloeng Bora · Reviewed: 2026-10-24 · Branch: `feature/complete-roadmap`

## Sources and limits of this review

- **Source used:** the requirements as the repository records them: the ERD (16 models named "from the assignment"
  in `app/models.py`), the roles and permissions in `app/seed.py`, the KPI list on the dashboard, `README.md` and
  `docs/roadmap.md`.
- **Not found:** the assignment brief itself and the "coverage map in Notion" that the roadmap mentions. A search of
  the connected Notion workspace did not find either. **Before submission, compare this table with the official
  assignment text** and add any requirement that is missing here.
- **Scope gap, needs a team decision:** `bora_section.docx` (the proposal section, 20 August) describes a
  *task management* bot: create, assign and track tasks with deadlines; admin, manager and member roles;
  Node.js / Telegraf. The system that was built (September onwards) is a *customer support* chatbot with an admin
  dashboard (FAQ, Knowledge Base, AI, human handoff) in Python. Either the proposal text must be updated to describe
  the built system, or the team must confirm with the lecturer which scope is graded. Reminders, notifications, roles
  and AI answers exist in both. Task creation, assignment and deadlines for *project tasks* do not exist in the code.

Status: ✅ done and covered by an automated test · 🟡 done, partly verified (see note) · ❌ not done

## Coverage

| # | Requirement | Where in the code | Test | Status |
|---|---|---|---|---|
| 1 | Bot authentication (token checked on start) | `app/bot/runtime.py` `prepare_bot` | - | 🟡 needs a real token run |
| 2 | Long Polling | `app/bot/main.py` | - | 🟡 needs a real token run |
| 3 | Webhook mode with secret check | `app/web/webhook.py` | `test_webhook.py` | ✅ (mocked Telegram) |
| 4 | `/start` (register user, choose language), `/help`, `/menu`, `/cancel` | `app/bot/handlers.py` | `test_bot_handlers.py`, `test_intents_forms.py` | ✅ |
| 5 | Custom commands managed by admins | `handlers.custom_command`, `/commands` page | `test_web.py` | ✅ |
| 6 | Main menu (Reply Keyboard), Inline Keyboards, Callback Query | `app/bot/keyboards.py` | `test_bot_handlers.py` | ✅ |
| 7 | Khmer and English | `app/i18n.py`, `language` on users, FAQ, KB, phrases | `test_routing.py::test_faq_khmer`, `test_intents_forms.py::test_khmer_intent` | ✅ |
| 8 | Response routing: Command → Rule → Intent → FAQ → Knowledge Base → AI → Fallback → Handoff | `app/services/router.py` | `test_routing.py` | ✅ |
| 9 | Keyword / rule responses | `app/services/rules.py` | `test_routing.py::test_keyword_rule` | ✅ |
| 10 | Intent detection with training phrases | `app/services/intents.py`, `/intents` page | `test_intents_forms.py` | ✅ |
| 11 | Entity extraction (phone, email, date, number) | `app/services/validators.py` | `test_validators.py` | ✅ |
| 12 | FAQ by category, with keywords, priority and status | `router.find_faq`, `/faq` page, FAQ menu | `test_bot_handlers.py`, `test_web.py` | ✅ |
| 13 | Knowledge Base articles | `router.find_article`, `/knowledge` page | `test_routing.py::test_knowledge_base` | ✅ |
| 14 | AI answers with System Prompt, KB context, timeout, retry, error handling | `app/services/ai.py`, Settings → AI | `test_ai.py` | 🟡 the AI key in `.env` has **expired** (HTTP 401 on 2026-10-24); tested with a mocked API only |
| 15 | Fallback + unknown question detection | `router.save_unknown_question`, dashboard list | `test_routing.py` | ✅ |
| 16 | Form conversation (Name → Phone → Email → Request → Confirmation) | `app/services/forms.py` | `test_intents_forms.py` | ✅ |
| 17 | Input validation and invalid input handling | `validators.py`, `forms.py` | `test_validators.py`, `test_intents_forms.py` | ✅ |
| 18 | Human handoff: queue, assign agent, statuses Open → Assigned → In Progress → Resolved → Closed | `app/services/handoff.py`, `/conversations` | `test_handoff.py`, `test_end_to_end.py` | ✅ |
| 19 | Agent replies from the dashboard reach the user | `handoff.agent_reply`, `services/telegram.py` | `test_web_roles.py`, `test_end_to_end.py` | 🟡 mocked Telegram |
| 20 | Feedback (thumbs and 1-5 stars) | `handlers.on_feedback` | `test_bot_handlers.py` | ✅ |
| 21 | Notifications: welcome, reminder, support reply, status | `app/services/notifications.py`, `scheduler.py` | `test_broadcast_notifications.py`, `test_handoff.py` | ✅ |
| 22 | Broadcast: audience, preview, schedule, history | `app/services/broadcast.py`, `/broadcast` | `test_broadcast_notifications.py`, `test_web_roles.py` | ✅ |
| 23 | Image, document, voice, location messages stored; unsupported types answered | `handlers.on_media`, `on_unsupported` | `test_bot_handlers.py` | ✅ |
| 24 | Blocked / suspended users, maintenance mode | `handlers._allowed`, Settings | `test_bot_handlers.py`, `test_web.py` | ✅ |
| 25 | Rate limit, spam detection, content moderation | `app/services/moderation.py`, `ProtectionMiddleware` | `test_moderation.py` | ✅ (prototype, in memory) |
| 26 | Retry for Telegram API errors | `services/telegram.py` `RetryMiddleware` | `test_telegram_retry.py` | ✅ |
| 27 | Admin login, session, auto logout, lockout, CSRF | `app/web/deps.py`, `routes/auth.py` | `test_web.py`, `test_web_roles.py` | ✅ |
| 28 | Roles and permissions (Administrator, Bot Manager, Content Manager, Support Agent, Viewer) | `deps.require`, Settings → Roles | `test_web_roles.py` | ✅ |
| 29 | Data masking of Telegram user data by role | `app/services/masking.py` | `test_web_roles.py` | ✅ |
| 30 | Activity, Conversation, Audit and Error logs | `app/services/logs.py`, `/logs` | `test_logs.py` | ✅ |
| 31 | Dashboard statistics and KPIs (resolution, AI answer, fallback, handoff, satisfaction) | `app/services/stats.py` | `test_stats.py` | ✅ |
| 32 | Dashboard charts (user growth, incoming vs outgoing, popular questions) | `stats.chart_data`, `dashboard.html` | `test_stats.py` (data only) | 🟡 charts checked by eye |
| 33 | Reports with PDF and Excel export (Khmer text) | `app/services/reports.py`, `/reports` | `test_web.py::test_reports_export` | ✅ |
| 34 | Settings: bot info, AI settings, System Prompt, maintenance mode, roles, accounts | `routes/settings.py` | `test_web.py` | ✅ |
| 35 | Responsive dashboard (tablet, mobile) | `static/style.css` | - | 🟡 checked by eye at 390 px and 1366 px |
| 36 | Database migrations | `migrations/`, `app/db.py` | `test_migrations.py` | ✅ |
| 37 | PostgreSQL | `asyncpg`, `docker-compose.yml`, `scripts/copy_database.py` | `test_copy_database.py` (SQLite → SQLite) | 🟡 **not yet run against a real PostgreSQL server** |
| 38 | Backup and recovery | `scripts/backup.py` | `test_backup.py` | ✅ (SQLite; PostgreSQL path untested) |
| 39 | Secrets kept out of code | `.env`, `.env.example`, `.gitignore` | - | ✅ |
| 40 | Each ERD model is used | `app/models.py` (all 16 + `UnknownQuestion`) | - | ✅ every table is read and written by a feature |

**Result:** 40 requirements found. 33 are done and covered by tests, 7 are done but only partly verified, and none are missing.
The items still open before the final demo are:

1. Run the bot with a real `BOT_TOKEN` once and walk through `docs/demo-script.md` (items 1, 2 and 19).
2. Get a new AI key (OpenRouter or another OpenAI-compatible API) and check one real AI answer (item 14).
3. Run `scripts/copy_database.py` once against PostgreSQL from `docker-compose.yml` (item 37).
4. Settle the proposal scope gap above.

## KPI definitions (as implemented)

| KPI | Definition |
|---|---|
| Resolution Rate | Conversations with at least one text message that were resolved: either an agent marked the support request Resolved, or the bot answered the last question without a fallback, no human was needed and nobody rated it 1-2. See `app/services/stats.py`. |
| Bot Answer Rate | Incoming questions that got a non-fallback answer (the old message-level number). |
| AI Answer Rate | Answers from the AI ÷ incoming questions. |
| Fallback Rate | Fallback answers ÷ incoming questions. |
| Human Handoff Rate | Conversations with a support request ÷ all conversations. |
| Satisfaction | Average feedback rating (1-5). |

## Answer quality (labelled test questions)

`python -m scripts.evaluate_questions` runs the 54 labelled questions in `docs/evaluation/test_questions.csv`
(39 English, 15 Khmer) through the routing on a throwaway database with all mock FAQs, without AI.

| Run | Passed | English | Khmer |
|---|---|---|---|
| First run | 47 / 53 (89%) | 33 / 38 | 14 / 15 |
| After fixing 2 wrong labels, the keyword ranking and one keyword | 52 / 54 (96%) | 37 / 39 | 15 / 15 |

Findings:

- **Fixed:** when two FAQ keywords matched, the first FAQ won even when its keyword was short and generic
  ("open" beat "saturday"; "how do i register" beat "register for my son"). Longer keywords now win.
- **Fixed:** "i missed a class" did not match the keyword "missed class"; the keyword "missed a class" was added.
- **Open, needs a team decision:** "How do I book an appointment?" is answered by the `book_appointment` intent
  ("we noted your appointment for -") instead of the FAQ that explains how to book. Options: remove the FAQ, or keep
  how-to wording out of the intent's training phrases so that how-to questions reach the FAQ.
- **Open:** the Knowledge Base article "Refund policy" is never reached, because the FAQ "Can I get a refund?"
  answers every refund question first. Merge them, or give the article keywords the FAQ does not have.

These questions were **written by the team**, not collected from real users. They are a starting set; the real
questions from the demo users (Dashboard → Top unanswered questions, Reports → Top questions) should be added to the
CSV before the final evaluation.
