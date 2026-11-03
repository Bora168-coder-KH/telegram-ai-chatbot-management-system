# Demo capture (screenshots and bot texts for the draft video)

These scripts play the video story through the **real project code** and save what it shows:

- `server.py` — runs the real dashboard. Telegram is replaced by a recorder (`outbox.json`), so no bot token is needed.
- `students.py 1` — Sokha and six other demo students talk to the real bot handlers. `students.py 2` — "Student B" asks the bus question after the new FAQ exists. Replies go to `transcript.json`.
- `admin.js A` / `admin.js B` — Dara's steps in a real browser (Playwright): login, queue, reply, Resolved, Add FAQ, broadcast, reports, roles, Viewer. Screenshots go to `shots/`, highlight boxes to `boxes.json`.

## One way to run it

From the project root, on branch `feature/all-screens`, with the packages installed:

```bash
export DATABASE_URL="sqlite+aiosqlite:///$PWD/story.db" BOT_TOKEN="" AI_API_KEY="" ADMIN_PASSWORD="demo-password-1" ADMIN_EMAIL="dara@university.example" SECRET_KEY="story-secret" PYTHONPATH="$PWD"
```

Then run, in order: `python server.py &`, `python students.py 1`, `node admin.js A`, `python students.py 2`, `node admin.js B`.

Notes:
- The dashboard loads HTMX and Chart.js from a CDN. `admin.js` serves local copies, because the capture computer may be offline.
- Install a Khmer font (Noto Sans Khmer is in `app/web/static/fonts/`) or Khmer shows as boxes in the browser.
- `admin.js` adds blank space under two pages only for the screenshots, so a table row can be centred.
