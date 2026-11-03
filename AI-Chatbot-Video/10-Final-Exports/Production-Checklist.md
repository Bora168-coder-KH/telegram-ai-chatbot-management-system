# Part 6 — Final Production Checklist

Output order: **10. Final production checklist**.

## A. Changes from the original Khmer script (please approve)

I kept every idea from the original script. I changed a few words only where the old wording did not match the real software, or where the spelling was wrong.

| Scene | Original | New | Why |
|---|---|---|---|
| SC-015 | បង្កើត **កែប្រែ** និងរក្សាទុក | បង្កើត **គ្រប់គ្រង** និងរក្សាទុក | The code can add, disable/enable and delete FAQs, but it has **no button to edit the FAQ text**. If the team adds an Edit button before recording, change the word back. |
| SC-032 | ស្ថិតក្នុង**ជួរស្ថិតិ**របស់គាត់ | កំពុងរង់ចាំក្នុង**ជួរ**របស់គាត់ | The request waits in the support **queue** (Conversations page), not in the statistics. |
| SC-036 | សំណួរត្រូវបានចាប់យកពី**ការសន្ទនា**របស់សុខា | សំណួររបស់សុខាត្រូវបានបំពេញរួចដោយស្វ័យប្រវត្តិ | Add FAQ is on the Dashboard's "Top unanswered questions" list. The question there came from Sokha's chat. |
| SC-041 | ទាញយករបាយការណ៍**ជាភាសាខ្មែរ** | ទាញយករបាយការណ៍ជា PDF ឬ Excel ដោយ**អក្សរខ្មែរបង្ហាញបានត្រឹមត្រូវ** | The report labels are in English. Khmer questions and answers inside the report print correctly. |
| SC-005, SC-019 | — | Short purpose and benefit lines | Your brief asked for the purpose (Chapter 1) and the benefits (Chapter 3). They only repeat ideas already in the script. |
| SC-046 | — | "Not a large public benchmark" | Your brief asked for this. |

**Spelling fixes:** អេសុីលីដា → អេស៊ីលីដា · ផ្ញើរ → ផ្ញើ · អាធ្រាត → អធ្រាត្រ · បញ្ចល → បញ្ចូល · កាសន្ទនា → ការសន្ទនា · ការរធ្វើ → ការធ្វើ · វានិង → វានឹង

## B. Please confirm these facts

- [ ] **Names.** The project README says "Lay Sopanha" and "Tan Mengkoung". The script says "Panhna" and "Mengkuang". Use the spelling each person prefers, in both languages.
- [ ] **Lecturer's name** in English and Khmer: Keo Tongheng / កែវ តុងហេង.
- [ ] **University logo:** use it only if your faculty allows it.
- [ ] **Demo FAQ answers are sample data** (for example `www.example.com`). Replace the answers you show (documents, bus) with true university information, or say on screen that it is demo data.

## C. Before recording the software

- [ ] Use the code on branch **`feature/all-screens`**. The `main` branch is the older starter and does not have the dashboard reply, broadcast, reports, roles or masking.
- [ ] `pytest` passes. `python -m app.mock_data` loaded the FAQs.
- [ ] Two Telegram test accounts: "Sok Sokha" (new account, so it asks for the language) and "Student B".
- [ ] One **Administrator** account and one **Viewer** account in Settings.
- [ ] Rehearse these exact messages first:
  - SC-021: `តើចុះឈ្មោះចូលរៀន ត្រូវការឯកសារអ្វីខ្លះ?` → Khmer documents answer
  - SC-025: `What are the required documents for registration?` → English documents answer
  - SC-026: `I want to book an appointment on 2026-12-15` → "We noted your appointment request for 2026-12-15"
  - SC-027: `Is there a bus to campus?` → fallback with three buttons
  - SC-037: new FAQ with keywords `bus to campus, shuttle bus, campus bus` (not just `bus`: it also matches "business")
  - SC-038: `Is there a shuttle bus to the campus?` from "Student B" → the new answer
- [ ] If a Khmer message does not match, type it again without hidden spaces (some Khmer keyboards add zero-width spaces).
- [ ] Keep the order: after Sokha asks for human support, the bot waits for the agent and does not answer her until Dara marks the request Resolved.
- [ ] Do not use "Do you have a dormitory?" as the unknown question. The team's test found the bot answers it wrongly.
- [ ] The date in SC-026 must still be in the future on the day you show the video.
- [ ] **Fix the Broadcast page bug before recording SC-040.** Found while making the draft video: in a real browser, the
      message box clears itself about 0.4 s after you stop typing, and the "Preview" button asks "Send this broadcast?".
      Cause: in `app/web/templates/broadcast.html` the form's `hx-on::after-request` runs after *every* request inside
      the form (also the live preview), and the form's `hx-confirm` is inherited by the preview elements.
      One fix: add `hx-disinherit="hx-confirm"` to the `<form>`, and change the reset condition to
      `if (event.detail.successful && event.detail.elt === this) { … }`. The broadcast service itself works
      (the draft video shows a real 8 / 8 delivery).

## D. Privacy and honesty

- [ ] Blur emails, phone numbers, Telegram IDs, the bot token, passwords and any real student data.
- [ ] Sokha and Dara are marked as fictional (SC-006, SC-009, SC-049).
- [ ] No AI image or video of a real person (presenter, team, lecturer).
- [ ] The video never says the AI "learns" or "retrains" by itself. Knowledge grows when staff add FAQs.
- [ ] The test result says "our own 57 test questions", not a public benchmark.

## E. Quality control (checked while writing this plan)

| Check | Result |
|---|---|
| All lines of the original script are in the storyboard | ✅ Every sentence maps to SC-002 → SC-048 |
| Khmer and English say the same thing | ✅ Same scenes, same facts, same order |
| Scene order is logical | ✅ Problem → solution → student → staff → results |
| Characters stay the same | ✅ One fixed character block reused in every AI prompt |
| Software features are real | ✅ Each feature was checked in the code (branch `feature/all-screens`) — see section A for the one gap |
| Narration matches the visuals | ✅ Each scene has one action and one matching sentence |
| Time to read captions | ✅ Each scene is at least 1 s longer than the estimated voice |
| Statistics are correct | ✅ 53 + 4 = 57 · 53 ÷ 57 = 0.92982… ≈ **92.98%** · 42 English + 15 Khmer = 57 |
| Suitable for university assessment | ✅ Clear structure, honest limits, real demo |
| Each scene can be edited alone | ✅ One ID per scene, used in every file name |

## F. Before export

- [ ] Replace the estimated subtitle times with real times after recording the voice (CapCut: Auto captions, then paste the text from the script; DaVinci: import the SRT and move cues to the waveform).
- [ ] Watch the full video once with sound off: can you follow it from captions only?
- [ ] Watch once with eyes closed: is the voice clear and the music quiet enough?
- [ ] Check Khmer text in every title and subtitle (no broken vowels).
- [ ] Export: 1920×1080, 25 fps, H.264, about 12–16 Mbps, AAC 192 kbps.
- [ ] Files: `AI-Chatbot-Video-KH.mp4` and `AI-Chatbot-Video-EN.mp4`.
