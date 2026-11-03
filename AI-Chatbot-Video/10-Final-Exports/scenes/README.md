# Scene files

Each scene of the draft video as its own file, so you can replace one scene without touching the rest.

- **Khmer:** `Khmer/SC-0XX-KH.mp4` · **English:** `English/SC-0XX-EN.mp4`
- 1920×1080, 25 fps, cut frame-exactly from the full videos in `10-Final-Exports/`.
- The full videos `AI-Chatbot-Video-KH.mp4` and `AI-Chatbot-Video-EN.mp4` were **not changed**.
- Put the scenes back together in CapCut or DaVinci Resolve in ID order (SC-001 → SC-049).

## Change one scene later (one method)

1. Edit the scene in `09-Editing-Project/remotion-draft/src/scenes/Scenes.tsx` (search for `S022`, for example).
2. In `09-Editing-Project/remotion-draft/`, run `npm install` once, then:

```bash
./render-scene.sh SC-022 KH
```

3. Check `out/SC-022-KH.mp4`. If you like it, copy it over `10-Final-Exports/scenes/Khmer/SC-022-KH.mp4`.

## Scene list

| Scene | Chapter | Title | Starts at | Length | Khmer file | English file |
|---|---|---|---|---|---|---|
| SC-001 | 1. Introduction | Opening title | 0:00 | 5 s | `Khmer/SC-001-KH.mp4` | `English/SC-001-EN.mp4` |
| SC-002 | 1. Introduction | Greeting and presenter | 0:05 | 13 s | `Khmer/SC-002-KH.mp4` | `English/SC-002-EN.mp4` |
| SC-003 | 1. Introduction | Team 1 | 0:18 | 8 s | `Khmer/SC-003-KH.mp4` | `English/SC-003-EN.mp4` |
| SC-004 | 1. Introduction | Project and supervisor | 0:26 | 12 s | `Khmer/SC-004-KH.mp4` | `English/SC-004-EN.mp4` |
| SC-005 | 1. Introduction | Purpose and welcome | 0:38 | 14 s | `Khmer/SC-005-KH.mp4` | `English/SC-005-EN.mp4` |
| SC-006 | 2. The Problem | Meet Sokha | 0:52 | 10 s | `Khmer/SC-006-KH.mp4` | `English/SC-006-EN.mp4` |
| SC-007 | 2. The Problem | Midnight message | 1:02 | 8 s | `Khmer/SC-007-KH.mp4` | `English/SC-007-EN.mp4` |
| SC-008 | 2. The Problem | No reply at midnight | 1:10 | 7 s | `Khmer/SC-008-KH.mp4` | `English/SC-008-EN.mp4` |
| SC-009 | 2. The Problem | Meet Dara | 1:17 | 7 s | `Khmer/SC-009-KH.mp4` | `English/SC-009-EN.mp4` |
| SC-010 | 2. The Problem | A full inbox | 1:24 | 11 s | `Khmer/SC-010-KH.mp4` | `English/SC-010-EN.mp4` |
| SC-011 | 2. The Problem | Answering by hand | 1:35 | 6 s | `Khmer/SC-011-KH.mp4` | `English/SC-011-EN.mp4` |
| SC-012 | 2. The Problem | Tired | 1:41 | 5 s | `Khmer/SC-012-KH.mp4` | `English/SC-012-EN.mp4` |
| SC-013 | 2. The Problem | The wish | 1:46 | 8 s | `Khmer/SC-013-KH.mp4` | `English/SC-013-EN.mp4` |
| SC-014 | 3. Our Solution | Our solution | 1:54 | 13 s | `Khmer/SC-014-KH.mp4` | `English/SC-014-EN.mp4` |
| SC-015 | 3. Our Solution | Managing FAQs | 2:07 | 9 s | `Khmer/SC-015-KH.mp4` | `English/SC-015-EN.mp4` |
| SC-016 | 3. Our Solution | Khmer and English | 2:16 | 6 s | `Khmer/SC-016-KH.mp4` | `English/SC-016-EN.mp4` |
| SC-017 | 3. Our Solution | Different words, same meaning | 2:22 | 7 s | `Khmer/SC-017-KH.mp4` | `English/SC-017-EN.mp4` |
| SC-018 | 3. Our Solution | Honest when it does not know | 2:29 | 11 s | `Khmer/SC-018-KH.mp4` | `English/SC-018-EN.mp4` |
| SC-019 | 3. Our Solution | Good for both sides | 2:40 | 9 s | `Khmer/SC-019-KH.mp4` | `English/SC-019-EN.mp4` |
| SC-020 | 4. Student Experience | /start and Khmer | 2:49 | 8 s | `Khmer/SC-020-KH.mp4` | `English/SC-020-EN.mp4` |
| SC-021 | 4. Student Experience | The same question, again | 2:57 | 7 s | `Khmer/SC-021-KH.mp4` | `English/SC-021-EN.mp4` |
| SC-022 | 4. Student Experience | Instant answer | 3:04 | 6 s | `Khmer/SC-022-KH.mp4` | `English/SC-022-EN.mp4` |
| SC-023 | 4. Student Experience | Feedback 👍 | 3:10 | 5 s | `Khmer/SC-023-KH.mp4` | `English/SC-023-EN.mp4` |
| SC-024 | 4. Student Experience | Switch to English | 3:15 | 5 s | `Khmer/SC-024-KH.mp4` | `English/SC-024-EN.mp4` |
| SC-025 | 4. Student Experience | Different words, still understood | 3:20 | 11 s | `Khmer/SC-025-KH.mp4` | `English/SC-025-EN.mp4` |
| SC-026 | 4. Student Experience | Capturing a date | 3:31 | 10 s | `Khmer/SC-026-KH.mp4` | `English/SC-026-EN.mp4` |
| SC-027 | 4. Student Experience | A question the bot does not know | 3:41 | 6 s | `Khmer/SC-027-KH.mp4` | `English/SC-027-EN.mp4` |
| SC-028 | 4. Student Experience | No guessing | 3:47 | 8 s | `Khmer/SC-028-KH.mp4` | `English/SC-028-EN.mp4` |
| SC-029 | 4. Student Experience | Asking for a human | 3:55 | 9 s | `Khmer/SC-029-KH.mp4` | `English/SC-029-EN.mp4` |
| SC-030 | 5. Administrator Experience | Next morning: login | 4:04 | 6 s | `Khmer/SC-030-KH.mp4` | `English/SC-030-EN.mp4` |
| SC-031 | 5. Administrator Experience | Statistics and unanswered questions | 4:10 | 8 s | `Khmer/SC-031-KH.mp4` | `English/SC-031-EN.mp4` |
| SC-032 | 5. Administrator Experience | Sokha's request in the queue | 4:18 | 6 s | `Khmer/SC-032-KH.mp4` | `English/SC-032-EN.mp4` |
| SC-033 | 5. Administrator Experience | The whole conversation | 4:24 | 8 s | `Khmer/SC-033-KH.mp4` | `English/SC-033-EN.mp4` |
| SC-034 | 5. Administrator Experience | Reply to Telegram | 4:32 | 8 s | `Khmer/SC-034-KH.mp4` | `English/SC-034-EN.mp4` |
| SC-035 | 5. Administrator Experience | Marked as Resolved | 4:40 | 6 s | `Khmer/SC-035-KH.mp4` | `English/SC-035-EN.mp4` |
| SC-036 | 5. Administrator Experience | Add FAQ — question filled in | 4:46 | 9 s | `Khmer/SC-036-KH.mp4` | `English/SC-036-EN.mp4` |
| SC-037 | 5. Administrator Experience | Type the answer and save | 4:55 | 8 s | `Khmer/SC-037-KH.mp4` | `English/SC-037-EN.mp4` |
| SC-038 | 5. Administrator Experience | Another student, different words | 5:03 | 8 s | `Khmer/SC-038-KH.mp4` | `English/SC-038-EN.mp4` |
| SC-039 | 5. Administrator Experience | Yesterday unknown, today answered | 5:11 | 7 s | `Khmer/SC-039-KH.mp4` | `English/SC-039-EN.mp4` |
| SC-040 | 5. Administrator Experience | Broadcast | 5:18 | 7 s | `Khmer/SC-040-KH.mp4` | `English/SC-040-EN.mp4` |
| SC-041 | 5. Administrator Experience | Report export | 5:25 | 8 s | `Khmer/SC-041-KH.mp4` | `English/SC-041-EN.mp4` |
| SC-042 | 5. Administrator Experience | Account permissions | 5:33 | 6 s | `Khmer/SC-042-KH.mp4` | `English/SC-042-EN.mp4` |
| SC-043 | 5. Administrator Experience | The Viewer role | 5:39 | 9 s | `Khmer/SC-043-KH.mp4` | `English/SC-043-EN.mp4` |
| SC-044 | 6. Results and Conclusion | Before and after | 5:48 | 10 s | `Khmer/SC-044-KH.mp4` | `English/SC-044-EN.mp4` |
| SC-045 | 6. Results and Conclusion | Test results | 5:58 | 13 s | `Khmer/SC-045-KH.mp4` | `English/SC-045-EN.mp4` |
| SC-046 | 6. Results and Conclusion | What the test means | 6:11 | 10 s | `Khmer/SC-046-KH.mp4` | `English/SC-046-EN.mp4` |
| SC-047 | 6. Results and Conclusion | Next step | 6:21 | 9 s | `Khmer/SC-047-KH.mp4` | `English/SC-047-EN.mp4` |
| SC-048 | 6. Results and Conclusion | Thank you | 6:30 | 10 s | `Khmer/SC-048-KH.mp4` | `English/SC-048-EN.mp4` |
| SC-049 | 6. Results and Conclusion | End card | 6:40 | 6 s | `Khmer/SC-049-KH.mp4` | `English/SC-049-EN.mp4` |
