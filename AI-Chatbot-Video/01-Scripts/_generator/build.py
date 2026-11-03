# -*- coding: utf-8 -*-
"""Build every production document and the two SRT files from scenes.py."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from scenes import CHAPTERS, DARA, HOME_NIGHT, NEGATIVE, OFFICE, SCENES, SOKHA, STYLE  # noqa: E402

OUT = Path(sys.argv[1])

def mmss(sec: float) -> str:
    sec = int(round(sec))
    return f"{sec // 60}:{sec % 60:02d}"


def srt_time(sec: float) -> str:
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s_, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s_:02d},{ms:03d}"


def plain(text: str) -> str:
    """Narration without pause marks and subtitle breaks."""
    text = text.replace(" | ", " ").replace("//", "").replace(" / ", " ").replace("/start", "\u0000")
    text = text.replace("/", "").replace("\u0000", "/start")
    return re.sub(r"\s+", " ", text).strip()


def spoken(text: str) -> str:
    """Narration for the voice script: keep pauses, drop subtitle breaks."""
    return re.sub(r"\s+", " ", text.replace(" | ", " ")).strip()


def en_seconds(text: str) -> float:
    return len(plain(text).split()) / 2.5  # about 150 words per minute


def kh_seconds(text: str) -> float:
    # Khmer: count base consonants and independent vowels (≈ syllables), about 5.5 per second.
    # A consonant after the coeng sign (U+17D2) is a subscript, not a new syllable.
    text = re.sub("្[ក-អ]", "", plain(text))
    syllables = len(re.findall("[ក-ឳ]", text))
    latin_words = len(re.findall(r"[A-Za-z0-9]+", text))
    return syllables / 5.5 + latin_words / 2.5


import math

for s in SCENES:
    s["en_vo"] = round(en_seconds(s["en"]), 1) if s["en"] else 0
    s["kh_vo"] = round(kh_seconds(s["kh"]), 1) if s["kh"] else 0
    # One shared timeline: the scene must fit the longer voice + 1 s of breathing room.
    s["dur"] = max(s["dur"], math.ceil(max(s["en_vo"], s["kh_vo"]) + 1.0))

t = 0.0
for s in SCENES:
    s["start"], s["end"] = t, t + s["dur"]
    t += s["dur"]
TOTAL = t


def fill(prompt: str) -> str:
    return prompt.format(SOKHA=SOKHA, DARA=DARA, HOME_NIGHT=HOME_NIGHT, OFFICE=OFFICE)


def full_prompt(s) -> str:
    return f"{fill(s['prompt']).strip()} {STYLE}\n\nNegative prompt: {NEGATIVE}"


def chapter_scenes(ch):
    return [s for s in SCENES if s["ch"] == ch]


def write(rel: str, text: str):
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def cap(text: str) -> str:
    return text.replace("\n", " / ") if text else "—"


# ---------------------------------------------------------------- 1–2 concept and structure
lines = [
    "# Part 1 — Video Concept and Story Structure",
    "",
    "Output order: **1. Concept** and **2. Six-chapter structure**. Scene IDs match every other file.",
    "",
    "## 1. Video concept",
    "",
    "**Title:** AI Chatbot Management System (Telegram Bot)",
    "",
    "**One-line idea:** A student gets no answer at midnight, and a staff member answers the same questions all day. "
    "Our Telegram bot and dashboard fix both problems — and we show the real working system.",
    "",
    "**Style:** Calm academic documentary. Short AI-generated story scenes (Sokha and Dara) + real screen recordings "
    "of Telegram and the dashboard + clean 2D motion graphics + the real presenter on camera.",
    "",
    "**Audience:** University lecturers, students and project evaluators.",
    "",
    "**Versions:** Version A (Khmer narration) and Version B (English narration). Same scenes, same order, "
    "same visuals. Only the voice-over, captions and a few language-specific graphics change.",
    "",
    f"**Recommended total duration:** about **{mmss(TOTAL)}** ({int(TOTAL)} seconds, {len(SCENES)} scenes). "
    "With slower Khmer reading, allow up to about 7:00.",
    "",
    "**Why this length:** it is long enough to show every feature in the original script one by one, "
    "but short enough for a class presentation slot.",
    "",
    "**Format:** 1920×1080 (16:9), 25 fps, stereo audio. Export H.264 MP4.",
    "",
    "**Typography (same in both versions):**",
    "- Headings: Newsreader (English) · Kantumruy Pro or Noto Serif Khmer (Khmer)",
    "- Captions and labels: Inter (English) · Kantumruy Pro (Khmer)",
    "- Colours: background #FAF9F6, cards #FFFFFF, text #111827, secondary text #4B5563, borders #E5E7EB, "
    "one muted accent (for example #1F5F7A) used only for highlights.",
    "",
    "**Honesty rules used in this plan:**",
    "- Sokha and Dara are fictional. The end card says so.",
    "- Every software scene uses the real system (branch `feature/all-screens`).",
    "- The bot's knowledge grows only because staff add verified FAQs. The video never says the AI retrains itself.",
    "- The results are from the team's own 57 test questions, not a public benchmark.",
    "",
    "## 2. Six-chapter story structure",
    "",
    "| Chapter | Scenes | Time | Duration | What the viewer learns |",
    "|---|---|---|---|---|",
]
purpose = {
    1: "Who we are, the project name, the supervisor, and the project's purpose.",
    2: "The real problem: no answers at night, and staff tired of repeated questions.",
    3: "The solution: a Telegram bot + a web dashboard, FAQs, two languages, honest fallback, human support.",
    4: "Sokha uses the bot: Khmer answer, 👍, English paraphrase, date capture, unknown question, human support.",
    5: "Dara uses the dashboard: stats, queue, reply, Resolved, Add FAQ, broadcast, reports, roles, Viewer masking.",
    6: "Before and after, the 57-question test result (≈ 92.98%), the next step, and thank you.",
}
for ch, (en_name, kh_name) in CHAPTERS.items():
    sc = chapter_scenes(ch)
    dur = sum(s["dur"] for s in sc)
    lines.append(f"| {ch}. {en_name} ({kh_name}) | {sc[0]['id']}–{sc[-1]['id']} | "
                 f"{mmss(sc[0]['start'])}–{mmss(sc[-1]['end'])} | {dur} s | {purpose[ch]} |")
lines += ["", f"**Total:** {mmss(TOTAL)}", ""]
lines += ["### Scene list", ""]
for ch, (en_name, kh_name) in CHAPTERS.items():
    lines.append(f"**Chapter {ch} — {en_name} ({kh_name})**")
    lines.append("")
    for s in chapter_scenes(ch):
        lines.append(f"- {s['id']} · {s['title']} · {s['dur']} s")
    lines.append("")
write("01-Scripts/01-Video-Concept-and-Structure.md", "\n".join(lines))

# ---------------------------------------------------------------- 3 characters
char = f"""# Part 2 — Reusable Character Reference Prompts

Output order: **3. Character reference prompts**.

## How to keep the faces the same (one simple method)

1. Generate **one reference image** for each character with the prompt below (front view, neutral background).
2. Pick the best image. Save it as `02-Character-References/Sokha-ref.png` and `Dara-ref.png`.
3. For every scene, use **image-to-video** (or "character reference" / "start frame") with that image, plus the scene prompt.
4. Never change the clothing words. Copy the full character block into every prompt.

**Why this works:** the AI tool copies the face, hair and clothes from the same picture each time, so it does not "invent" a new person.

## Sokha (សុខា) — fictional student applicant

**Character block (paste into every Sokha prompt):**

> {SOKHA}

**Reference image prompt:**

> Character reference sheet, photorealistic. {SOKHA} Full-body front view and a close-up portrait side by side, standing straight with a small friendly smile, plain light-grey studio background, soft even light, sharp focus on the face. No text, no logos.

**Keep the same:** face shape, black hair clip on the left, light-blue blouse, dark jeans, white sneakers, white phone case.

## Dara (ដារ៉ា) — fictional customer service staff member

**Character block (paste into every Dara prompt):**

> {DARA}

**Reference image prompt:**

> Character reference sheet, photorealistic. {DARA} Full-body front view and a close-up portrait side by side, standing straight with a calm, kind expression, plain light-grey studio background, soft even light, sharp focus on the face. No text, no logos.

**Keep the same:** glasses, side-parted hair, white shirt, navy lanyard with a blank card, silver watch on the left wrist.

## Shared settings

**Sokha's room (night):** {HOME_NIGHT}

**Help-desk office (day):** {OFFICE}

**Style line (add to every AI prompt):** {STYLE}

**Negative prompt (add to every AI prompt):** {NEGATIVE}

## Real people

Panhna (presenter), the team and Lecturer Keo Tongheng are real people. **Do not generate AI images or videos of them.** Film the presenter with a phone and use real team photos.
"""
write("02-Character-References/Character-Reference-Prompts.md", char)

# ---------------------------------------------------------------- 4 storyboard
lines = [
    "# Part 3 — Complete Bilingual Storyboard",
    "",
    "Output order: **4. Scene-by-scene storyboard**.",
    "",
    "- Times are planned edit times. Final times depend on the recorded voice.",
    "- `/` in narration = short pause (about 0.3 s). `//` = longer pause (about 0.8 s).",
    "- Full AI prompts here already include the character blocks. Section 7 repeats them as a copy-paste list.",
    "",
]
for ch, (en_name, kh_name) in CHAPTERS.items():
    lines += [f"## Chapter {ch} — {en_name} ({kh_name})", ""]
    for s in chapter_scenes(ch):
        lines += [
            f"### {s['id']} — {s['title']}",
            "",
            f"- **Chapter:** {ch}. {en_name}",
            f"- **Time:** {mmss(s['start'])}–{mmss(s['end'])} · **Estimated duration:** {s['dur']} s",
            f"- **Asset type:** {s['asset']}",
            "",
            f"**Khmer voice-over:** {spoken(s['kh']) if s['kh'] else '(no narration — music only)'}",
            "",
            f"**English voice-over:** {spoken(s['en']) if s['en'] else '(no narration — music only)'}",
            "",
            f"**Visual description:** {s['visual']}",
            "",
            "**AI video generation prompt:** " + (
                "\n\n```text\n" + full_prompt(s) + "\n```" if s["prompt"]
                else "Not needed — use the real recording, photos or motion graphics named above."),
            "",
            f"**On-screen text (KH):** {cap(s['cap_kh'])}",
            "",
            f"**On-screen text (EN):** {cap(s['cap_en'])}",
            "",
            f"**Audio:** {s['audio']}",
            "",
            f"**Transition:** {s['trans']}",
            "",
            f"**Editing notes:** {s['edit']}",
            "",
            f"**Source files:** {s['src']}",
            "",
            "---",
            "",
        ]
write("01-Scripts/02-Bilingual-Storyboard.md", "\n".join(lines))

# ---------------------------------------------------------------- 5–6 narration scripts
def script(lang: str) -> str:
    kh = lang == "KH"
    head = [
        "# កំណែ A — អត្ថបទនិទានកថាភាសាខ្មែរពេញលេញ" if kh else "# Version B — Full English Narration Script",
        "",
        ("Output order: **5. Full Khmer narration script**." if kh
         else "Output order: **6. Full English narration script**."),
        "",
        ("សញ្ញា៖ `/` = ឈប់ខ្លី (ប្រហែល ០,៣ វិនាទី) · `//` = ឈប់វែង (ប្រហែល ០,៨ វិនាទី)។ "
         "សូមអានយឺតៗ ច្បាស់ៗ ដូចនិយាយធម្មតា។" if kh else
         "Marks: `/` = short pause (about 0.3 s) · `//` = longer pause (about 0.8 s). "
         "Read slowly and clearly, like normal speech."),
        "",
        ("**ការអានលេខ (SC-045):** ៩២,៩៨ = «កៅសិបពីរ ក្បៀស កៅសិបប្រាំបី ភាគរយ»។" if kh else
         "**Number reading (SC-045):** 92.98 = “ninety-two point nine eight percent”."),
        "",
        f"Recording file names: `06-Voiceovers/{'Khmer' if kh else 'English'}/SC-0XX-{lang}.wav` (one file per scene).",
        "",
    ]
    for ch, (en_name, kh_name) in CHAPTERS.items():
        head += [f"## {'ជំពូក' if kh else 'Chapter'} {ch} — {kh_name if kh else en_name}", ""]
        for s in chapter_scenes(ch):
            text = s["kh"] if kh else s["en"]
            vo = s["kh_vo"] if kh else s["en_vo"]
            caption = s["cap_kh"] if kh else s["cap_en"]
            head += [
                f"### {s['id']} · {s['title']}",
                "",
                (f"- **រយៈពេលឈុត៖** {s['dur']} វិនាទី · **រយៈពេលនិយាយប្រហែល៖** {vo} វិនាទី" if kh else
                 f"- **Scene length:** {s['dur']} s · **Speaking time (estimate):** {vo} s"),
                (f"- **អក្សរលើអេក្រង់៖** {cap(caption)}" if kh else f"- **On-screen caption:** {cap(caption)}"),
                "",
                f"> {spoken(text)}" if text else ("> (គ្មានការនិទាន — តន្ត្រីតែប៉ុណ្ណោះ)" if kh else "> (No narration — music only)"),
                "",
            ]
    return "\n".join(head)


write("01-Scripts/Khmer/Script-KH.md", script("KH"))
write("01-Scripts/English/Script-EN.md", script("EN"))

# ---------------------------------------------------------------- 7 AI prompts
lines = [
    "# Part 4 — Individual AI Video Generation Prompts",
    "",
    "Output order: **7. AI video generation prompts**. Copy one block at a time into your AI video tool.",
    "",
    "**Settings for every clip:** 16:9, 1080p, 5–10 seconds, image-to-video with the character reference image "
    "(see `02-Character-References/`). Generate 2–3 takes and pick the most natural one.",
    "",
    "**Phone and laptop screens:** the prompts ask for a plain green screen. In the editor, replace it with the real "
    "recording. If the green is not clean, cut to the full-screen recording instead.",
    "",
    "**Save as:** `03-AI-Generated-Scenes/SC-0XX-AI.mp4` (add `-sokha`, `-dara` or `-broll` when a scene has two clips).",
    "",
]
for s in SCENES:
    if not s["prompt"]:
        continue
    chars = [n for n, key in (("Sokha", "{SOKHA}"), ("Dara", "{DARA}")) if key in s["prompt"]]
    lines += [
        f"## {s['id']} — {s['title']} ({s['dur']} s)",
        "",
        f"Characters: {', '.join(chars) if chars else 'none (B-roll or background)'} · File: {s['src']}",
        "",
        "```text",
        full_prompt(s),
        "```",
        "",
    ]
write("03-AI-Generated-Scenes/AI-Video-Prompts.md", "\n".join(lines))

# ---------------------------------------------------------------- 8 timeline
lines = [
    "# Part 5 — Video Editing Timeline and Production Plan",
    "",
    "Output order: **8. Video-editing timeline**.",
    "",
    f"## Master timeline (total {mmss(TOTAL)})",
    "",
    "| Scene | Start | End | Sec | Ch | Asset | Voice files | Scene exports |",
    "|---|---|---|---|---|---|---|---|",
]
for s in SCENES:
    vo = f"{s['id']}-KH.wav · {s['id']}-EN.wav" if s["kh"] else "— (music only)"
    lines.append(f"| {s['id']} {s['title']} | {mmss(s['start'])} | {mmss(s['end'])} | {s['dur']} | {s['ch']} | "
                 f"{s['asset']} | {vo} | {s['id']}-KH.mp4 · {s['id']}-EN.mp4 |")
lines += ["", "## Chapter totals", "", "| Chapter | Duration | Music |", "|---|---|---|"]
music = {1: "Cue A — soft, hopeful piano", 2: "Cue B — slow, quiet piano",
         3: "Cue C — light, steady, optimistic", 4: "Cue C (lower)", 5: "Cue C (new section)",
         6: "Cue D — warm, uplifting ending"}
for ch, (en_name, _) in CHAPTERS.items():
    lines.append(f"| {ch}. {en_name} | {sum(s['dur'] for s in chapter_scenes(ch))} s | {music[ch]} |")
lines += [
    "",
    "## Where each type of footage goes",
    "",
    "- **Real camera (presenter):** SC-002, SC-048.",
    "- **AI-generated scenes and B-roll:** " + ", ".join(s["id"] for s in SCENES if s["prompt"] and "AI" in s["asset"]) + ".",
    "- **Telegram recordings:** " + ", ".join(s["id"] for s in SCENES if "telegram" in s["asset"].lower()) + ".",
    "- **Dashboard recordings:** " + ", ".join(s["id"] for s in SCENES if "dashboard" in s["asset"].lower()) + ".",
    "- **2D motion graphics:** " + ", ".join(s["id"] for s in SCENES if "motion graphics" in s["asset"].lower()) + ".",
    "",
    "## Camera shots for AI scenes",
    "",
    "- Medium shot or medium close-up for emotion (SC-006, SC-008, SC-012, SC-013).",
    "- Over-the-shoulder close-up for typing (SC-007, SC-011).",
    "- Slow dolly-in or push-in only. No fast moves, no spinning cameras.",
    "",
    "## Suggested B-roll",
    "",
    "- University building exterior, morning (SC-002).",
    "- Empty corridor at sunrise (SC-001 background).",
    "- Students walking on campus, far away (SC-047).",
    "- A second student's hands holding a phone (SC-038, optional).",
    "",
    "## How to record the real system (one method)",
    "",
    "1. Use the code on branch `feature/all-screens`. Run `python -m app.mock_data` to load the bilingual FAQs.",
    "2. Create two Telegram test accounts: **\"Sok Sokha\"** and **\"Student B\"**. Create a **Viewer** admin account.",
    "3. **Phone:** use the phone's built-in screen recorder. Light mode, large text, Do Not Disturb on.",
    "4. **Dashboard:** record with OBS Studio at 1920×1080, browser zoom 125%, hide bookmarks and other tabs.",
    "5. Follow the order SC-020 → SC-043 in one session, so the data (date, bus question, request) stays connected.",
    "6. For split screens (SC-034, SC-035, SC-040), record the phone and the dashboard at the same time.",
    "7. Blur emails, phone numbers, Telegram IDs, the bot token and any real names.",
    "",
    "## Voice-over placement",
    "",
    "- One WAV file per scene and language. Start each voice clip **0.5 s after** the scene starts.",
    "- Leave **0.5 s** of silence before the cut. Do not let one scene's voice cross into the next.",
    "- Record in a quiet room with soft furniture, phone 20 cm from the mouth, same phone for every file.",
    "",
    "## Music and sound effects",
    "",
    "- Voice peaks around −6 dB. Music under voice about −20 dB to −24 dB. Raise music only when nobody speaks.",
    "- Use royalty-free music (for example the CapCut library or the YouTube Audio Library).",
    "- Sound effects: soft typing, a short message pop, soft clicks. Keep them quiet. Use generic sounds, "
    "not copied app sounds.",
    "",
    "## Captions",
    "",
    "- On-screen text (labels and titles) is in the storyboard for each scene.",
    "- Subtitles are in `08-Subtitles/`. Burn them in for the class video, or upload them as separate tracks.",
    "- Subtitle style: Inter / Kantumruy Pro, 40–44 px, white text on a 60% dark box, bottom centre.",
    "",
    "## Assemble the edit (CapCut or DaVinci Resolve)",
    "",
    "1. Create a 1920×1080, 25 fps project in `09-Editing-Project/`.",
    "2. Track V1: scene footage. V2: overlays and highlights. V3: titles. A1: voice. A2: music. A3: sound effects.",
    "3. Place scenes in ID order using the master timeline above.",
    "4. Build the Khmer version first. Then duplicate the project, swap the voice files, captions and the "
    "KH/EN graphics (SC-017, SC-045), and adjust scene lengths if the English voice is shorter.",
    "5. Export each scene alone when you need to replace it: `10-Final-Exports/scenes/SC-0XX-KH.mp4`.",
    "6. Export the full videos: `10-Final-Exports/AI-Chatbot-Video-KH.mp4` and `AI-Chatbot-Video-EN.mp4`.",
]
write("09-Editing-Project/Editing-Timeline.md", "\n".join(lines))

# ---------------------------------------------------------------- 9 SRT
def wrap(text: str, width: int) -> str:
    if len(text) <= width:
        return text
    words = text.split(" ")
    best, best_gap = None, 10**9
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        gap = abs(len(a) - len(b))
        if gap < best_gap:
            best, best_gap = (a, b), gap
    return "\n".join(best) if best else text


def build_srt(key: str, width: int) -> str:
    cues, n = [], 0
    for s in SCENES:
        if not s[key]:
            continue
        parts = [plain(p) for p in s[key].split(" | ") if plain(p)]
        start, end = s["start"] + 0.5, s["end"] - 0.4
        total_len = sum(len(p) for p in parts)
        t0 = start
        for i, p in enumerate(parts):
            t1 = end if i == len(parts) - 1 else t0 + (end - start) * len(p) / total_len
            n += 1
            cues.append(f"{n}\n{srt_time(t0)} --> {srt_time(t1 - 0.05)}\n{wrap(p, width)}\n")
            t0 = t1
    return "\n".join(cues)


(OUT / "08-Subtitles").mkdir(parents=True, exist_ok=True)
(OUT / "08-Subtitles/AI-Chatbot-Video-KH-ESTIMATED.srt").write_text(build_srt("kh", 46), encoding="utf-8")
(OUT / "08-Subtitles/AI-Chatbot-Video-EN-ESTIMATED.srt").write_text(build_srt("en", 42), encoding="utf-8")

# ---------------------------------------------------------------- report
for s in SCENES:
    flag = ""
    print(f"{s['id']} dur={s['dur']:>2} en={s['en_vo']:>4} kh={s['kh_vo']:>4}{flag}")
print("TOTAL", mmss(TOTAL), len(SCENES))
