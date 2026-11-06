# Flow charts

One flow chart file per feature group of the Telegram AI Chatbot Management System.
The charts follow the current code on `main` (they show what the code does, not an ideal design).
They are written in Mermaid, so GitHub and VS Code (with a Mermaid extension) draw them directly.

| # | File | Features |
|---|---|---|
| 01 | [Startup: polling and webhook](01-startup-polling-webhook.md) | Bot authentication, Long Polling, Webhook with secret check |
| 02 | [Update pipeline and protection](02-update-pipeline-protection.md) | Database session, rate limit, spam (auto-suspend), moderation, handler order, error handler |
| 03 | [Commands and media](03-commands-media.md) | User registration, blocked / maintenance check, `/start` + language, `/help`, `/menu`, `/cancel`, custom commands, media, unsupported messages |
| 04 | [Main Menu](04-main-menu.md) | 7 Reply Keyboard buttons, inline menu buttons, feedback |
| 05 | [FAQ browsing](05-faq-browse.md) | FAQ categories → questions → answer (inline keyboard) |
| 06 | [Response routing](06-response-routing.md) | Rule → Intent (+entities) → FAQ → Knowledge Base (+AI) → AI → Fallback + unknown questions |
| 07 | [Contact form](07-contact-form.md) | Name → Phone → Email → Request → Confirmation, validation, cancel, reminder |
| 08 | [Human handoff](08-human-handoff.md) | Support statuses, auto-assign, agent queue, agent replies |
| 09 | [Broadcast](09-broadcast.md) | Audience, preview, send now / schedule, throttled sending, cancel, history |
| 10 | [Notifications and scheduler](10-notifications-scheduler.md) | 5 notification types, delivery status, scheduler jobs |
| 11 | [Retry and error handling](11-retry-error-handling.md) | Telegram retry, AI retry, Error logs |
| 12 | [Admin login and security](12-admin-login-security.md) | Login, lockout, auto logout, CSRF, permissions, data masking |
| 13 | [Content management](13-content-management.md) | FAQ, Knowledge Base, Intents + training phrases + test, Commands |
| 14 | [Dashboard, users, reports, settings](14-dashboard-users-reports-settings.md) | KPIs and charts, unanswered questions, users, reports + export, settings, roles, accounts, logs, backup / restore, copy database |

## Requirement → chart

Numbers are the rows of [`docs/requirements-coverage.md`](../docs/requirements-coverage.md).

| Requirement rows | Chart |
|---|---|
| 1 Bot authentication, 2 Long Polling, 3 Webhook | 01 |
| 24 Blocked users and maintenance mode, 25 Rate limit / spam / moderation | 02, 03 |
| 4 `/start` `/help` `/menu` `/cancel`, 5 Custom commands, 23 Media and unsupported types | 03 |
| 6 Main menu, inline keyboards, callback queries, 20 Feedback | 04, 05 |
| 7 Khmer and English | 03, 04, 05, 06 |
| 12 FAQ by category | 05, 06, 13 |
| 8 Response routing, 9 Rules, 10 Intents, 11 Entities, 13 Knowledge Base, 14 AI, 15 Fallback + unknown questions | 06 |
| 16 Form conversation, 17 Input validation | 07 |
| 18 Human handoff, 19 Agent replies | 08 |
| 22 Broadcast | 09 |
| 21 Notifications | 10 |
| 26 Telegram retry | 11 |
| 27 Login, session, auto logout, lockout, CSRF, 28 Roles and permissions, 29 Data masking | 12 |
| 30 Logs, 31 KPIs, 32 Charts, 33 Reports + export, 34 Settings | 14 |
| 36 Migrations, 37 PostgreSQL, 38 Backup and recovery | 01 (migrations on start), 14 |
| 35 Responsive layout, 39 Secrets in `.env`, 40 Every ERD model used | not a flow (no chart) |

The database tables used by these flows are in [`database/`](../database/).
