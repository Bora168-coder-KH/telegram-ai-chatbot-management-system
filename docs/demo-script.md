# Final presentation and live demo script

About 15 minutes of talk and demo, then questions. Every demo step names the feature it shows and what the audience
should see, so whoever presents can check that the step worked.

## Before the presentation (the day before)

- [ ] `pip install -r requirements.txt`, then `pytest`: all tests pass.
- [ ] `.env` has a working `BOT_TOKEN`. Set `ADMIN_PASSWORD`. If AI is part of the demo, set a working `AI_API_KEY`
      and `AI_MODEL` (the current key has expired).
- [ ] `python -m scripts.backup backup`: keep a backup of the demo database.
- [ ] `python -m app.mock_data`: loads the 140 bilingual mock FAQs.
- [ ] Create a second account in Settings → Accounts: **Viewer** role (for the masking step) and one
      **Support Agent**.
- [ ] Two phones or Telegram Desktop windows: one "student" account, one for the presenter.
- [ ] Take screenshots of every page into `docs/screenshots/` as the fallback if the network fails.

Start, in two terminals:

```bash
python -m app.bot.main                 # the bot (Long Polling) and the scheduler
uvicorn app.web.main:app               # the dashboard: http://127.0.0.1:8000
```

## Storyline

| Time | Part | Presenter | Message |
|---|---|---|---|
| 0:00 | Problem | Ponloeng Bora | Students ask the same questions again and again (opening hours, payment, registration) in Khmer and English. Staff answer by hand, late, and nobody can see which questions are not answered. |
| 1:30 | Solution | Ponloeng Bora | A Telegram bot answers most questions immediately and in the user's language, hands the rest to a person, and an admin dashboard shows and improves the answers. |
| 2:30 | Live demo: the student | Phal Raksa | (steps 1-6 below) |
| 7:00 | Live demo: the staff | Lay Sopanha | (steps 7-12 below) |
| 11:00 | Architecture and security | Tan Mengkoung | `docs/architecture.md`: routing order, layers, migrations, webhook mode, roles, masking, logs, backup |
| 12:30 | Results and KPIs | Ponloeng Bora | KPI definitions, answer quality 52/54 on the labelled questions, what was fixed because of it (`docs/requirements-coverage.md`) |
| 14:00 | Limits and next steps | Ponloeng Bora | Prototype limits (in-memory rate limit, AI needs a paid/free key, PostgreSQL run pending), next steps |

## Demo steps

### The student (Telegram)

1. **Start and language.** Send `/start`, then choose ខ្មែរ.
   *Shows:* user registration, language choice, Reply Keyboard main menu.
   *Expect:* the Khmer welcome text and menu buttons.
2. **FAQ by category.** Tap 📚 FAQ → ការបង់ប្រាក់ (Payment) → a question.
   *Shows:* Inline Keyboard, Callback Query, Khmer FAQ.
   *Expect:* the answer with 👍 / 👎 under it. Tap 👍 (feedback is stored).
3. **Typed question, English.** Switch the language to English (🌐), then type `can i pay monthly instead of all at once`.
   *Shows:* FAQ matching on a paraphrase (difflib similarity + keywords).
   *Expect:* the installments answer.
4. **Intent with an entity.** Type `I want to book an appointment on 2026-11-02`.
   *Shows:* intent detection with training phrases and date extraction.
   *Expect:* "We noted your appointment request for 2026-11-02".
5. **Form with validation.** Tap 📝 Send a Request. Answer: name `R2` (rejected), `Sok Dara`, phone `123` (rejected),
   `012 345 678`, email `dara@example.com`, request `I need my certificate`, then ✅ Yes.
   *Shows:* the multi-step form, input validation, the confirmation step.
   *Expect:* error messages for the bad inputs, a summary, then "Thank you! Your request was sent…".
6. **Unknown question.** Type `my certificate has a wrong birth date`.
   *Shows:* fallback with Rephrase / Main Menu / Human Support buttons; the question is saved as unanswered.

### The staff (dashboard)

7. **Login and dashboard.** Log in as the Administrator.
   *Shows:* login, statistics cards, KPIs, the four charts, "Top unanswered questions" with the question from step 6.
8. **Support queue and reply.** Conversations → the request from step 5 is in the queue, auto-assigned. Open it: the
   timeline shows the whole chat and the form details. Type a reply and send it.
   *Expect:* the reply arrives on the student's phone within a second. Send a message from the phone: it appears in
   the timeline by itself (live updates every 5 s). The bot does not try to answer it; it only says once that the
   message was passed to the agent.
9. **Resolve.** Click → Resolved.
   *Expect:* the student gets "Your support request was marked as resolved…"; the Resolution Rate on the dashboard
   goes up.
10. **Improve the bot.** Dashboard → unanswered question → Add FAQ (the question is filled in), add an answer.
    Ask the same question again on the phone.
    *Expect:* the new FAQ answer.
11. **Broadcast.** Broadcast → message `Classes start on Monday`, audience All users (the student switched to English
    in step 3, so "Khmer users" would not include them), watch the live preview and recipient count, send.
    *Expect:* the message on the phone; the history shows 1 / 1 delivered.
12. **Reports, roles and masking.** Reports → Export PDF (Khmer text prints correctly) and Excel. Log out, log in as the
    **Viewer**: Users shows `S** D***` and `012***678`, there is no Settings or Broadcast menu, and Logs shows every
    admin action as an Audit log.

## If something goes wrong

- **No internet / Telegram blocked:** run `pytest -v tests/test_end_to_end.py`. It plays the whole student → agent →
  resolved story without Telegram. Then show the screenshots.
- **The AI does not answer:** that is expected without a working key; the bot falls back politely. Say so and move on.
- **Bad demo data:** `python -m scripts.backup restore backups/<file>.db` (stop both processes first).

## Likely questions

- *Why does the bot not always use AI?* Rules, intents and FAQ are free, fast and always correct for known
  questions; AI is only used when they do not answer, with the Knowledge Base as context.
- *What does "Resolved" mean in the Resolution Rate?* See the KPI table in `docs/requirements-coverage.md`.
- *How is personal data protected?* Roles without the reply permission see masked data, phone numbers and emails are
  kept out of question statistics, passwords are hashed with scrypt, every admin change is logged, and the session
  ends after 30 minutes of inactivity.
- *What happens with many users?* Broadcasts are throttled to Telegram's limit, the Telegram client retries on
  flood limits and network errors, and the database can move to PostgreSQL with `scripts/copy_database.py`.
