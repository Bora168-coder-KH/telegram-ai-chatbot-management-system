# -*- coding: utf-8 -*-
"""Single source of truth for every scene. build.py turns this into all documents and SRT files.

Narration: " | " marks a subtitle break. "/" in the scripts means a short pause (about 0.3 s).
"""

STYLE = (
    "Photorealistic documentary style, 16:9, 24 fps, soft natural light, smooth slow camera movement, "
    "realistic modern Cambodian setting, calm and natural acting, realistic skin texture, "
    "mostly neutral colours with warm tones."
)

NEGATIVE = (
    "No readable text, no letters on screens or signs, no logos, no watermarks, no subtitles, "
    "no holograms, no neon, no glowing effects, no lens flares, no extra fingers, "
    "no change of face, hairstyle or clothing, no exaggerated emotion, no fast camera moves."
)

SOKHA = (
    "SOKHA: a 20-year-old Cambodian woman with a friendly, natural look; warm light-brown skin; oval face; "
    "dark-brown eyes; shoulder-length straight black hair with a small side part and a plain black hair clip "
    "on the left side; light natural make-up. She wears a light-blue short-sleeve cotton blouse, dark-navy "
    "jeans and white canvas sneakers, and carries a beige canvas tote bag. She uses a smartphone with a "
    "plain white case."
)

DARA = (
    "DARA: a 28-year-old Cambodian man with a calm, professional look; warm medium-brown skin; short, neat "
    "black hair with a side part; clean-shaven; thin black rectangular glasses. He wears a white long-sleeve "
    "collared shirt, dark-grey trousers and black leather shoes, a navy-blue lanyard with a blank white staff "
    "card, and a silver wristwatch on his left wrist. He works on a silver laptop."
)

HOME_NIGHT = (
    "Sokha's small, tidy bedroom in a Phnom Penh apartment at night: a light-wood desk, a desk lamp with warm "
    "light, a few books, a beige document folder, and a window with softly blurred city lights."
)

OFFICE = (
    "A modern Cambodian university help-desk office in the morning: a light-wood counter and desk, white walls, "
    "a green potted plant, large windows with soft daylight, and one or two blurred colleagues far in the background."
)

# Each scene: id, ch, title, dur (seconds), kh, en (narration), cap_kh, cap_en, visual, prompt (None = no AI video),
# audio, trans, edit, asset, src (source files)
SCENES = [
    # ---------------- Chapter 1 — Introduction ----------------
    dict(
        id="SC-001", ch=1, title="Opening title", dur=5,
        kh="", en="",
        cap_kh="AI Chatbot Management System (Telegram Bot)\nក្រុមទី ១ · សាកលវិទ្យាល័យពាណិជ្ជសាស្ត្រ អេស៊ីលីដា",
        cap_en="AI Chatbot Management System (Telegram Bot)\nTeam 1 · ACLEDA University of Business",
        visual=("Off-white background (#FAF9F6). The project name fades in, large, in dark text (#111827). "
                "One smaller line appears below it. Behind the text, a very soft, blurred university corridor "
                "(optional AI plate at 20% opacity). No icons, no effects."),
        prompt=("Optional background plate. Slow push-in along an empty, clean, modern university corridor at "
                "sunrise. White walls, light-wood doors, soft morning light through tall windows. Shallow depth of "
                "field, no people. Calm, hopeful mood. " ),
        audio="Music cue A starts: soft, hopeful piano. No sound effects.",
        trans="Fade in from black (1 s). Cross-dissolve (0.5 s) into SC-002.",
        edit=("Title font: Newsreader or Instrument Serif, about 64 pt. Second line: Inter (English) or "
              "Kantumruy Pro (Khmer), 28 pt, colour #4B5563. Text animation: simple fade in, 0.8 s."),
        asset="2D motion graphics (+ optional AI background plate)",
        src="SC-001-AI-plate.mp4 (optional)",
    ),
    dict(
        id="SC-002", ch=1, title="Greeting and presenter", dur=11,
        kh=("ជម្រាបសួរលោកគ្រូ / និងសួស្តីអ្នកទាំងអស់គ្នា។ | ខ្ញុំបាទឈ្មោះ បញ្ញា / "
            "ជានិស្សិតនៃសាកលវិទ្យាល័យពាណិជ្ជសាស្ត្រ អេស៊ីលីដា / | "
            "ជំនាញវិទ្យាសាស្ត្រ និងវិស្វកម្មកំព្យូទ័រ។"),
        en=("Hello to our lecturer, / and hello everyone. | My name is Panhna. / "
            "I am a student at ACLEDA University of Business, / | "
            "majoring in Computer Science and Engineering."),
        cap_kh="បញ្ញា · អ្នកធ្វើបទបង្ហាញ\nជំនាញវិទ្យាសាស្ត្រ និងវិស្វកម្មកំព្យូទ័រ",
        cap_en="Panhna · Presenter\nComputer Science and Engineering",
        visual=("Start with 3 s of B-roll: a wide shot of a modern university building in the morning. "
                "Then cut to the real presenter, Panhna, in a medium shot, standing in a quiet classroom and "
                "speaking to the camera. A clean lower-third shows his name and major."),
        prompt=("Optional B-roll only (do not generate the presenter). Wide establishing shot of a modern "
                "Cambodian university campus in the morning: a clean white-and-glass building, tropical trees, "
                "a few students walking far away (small, not recognisable). Slow pan from left to right. "
                "Soft morning sunlight. Calm, professional mood. No signs, no logos, no readable text."),
        audio="Music cue A continues under the voice (about −20 dB below the voice). Light outdoor ambience on the B-roll.",
        trans="Straight cut from B-roll to presenter. Cut to SC-003 on the last word.",
        edit=("Film Panhna with a phone at 1080p or 4K, 25 or 30 fps, eye level, window light from the side. "
              "Lower-third: white box (#FFFFFF) with a thin #E5E7EB border, dark text. "
              "Use the official university logo only if your faculty allows it."),
        asset="Real camera footage (presenter) + optional AI B-roll + lower-third graphic",
        src="SC-002-CAM.mp4, SC-002-AI-broll.mp4 (optional)",
    ),
    dict(
        id="SC-003", ch=1, title="Team 1", dur=8,
        kh="ខ្ញុំបាទជាសមាជិកក្រុមទី ១ / ដែលមានសមាជិក ៤ នាក់ / | គឺ ខ្ញុំបាទ / បូរ៉ា / រក្សា / និង ម៉េងគ័ង។",
        en="I am a member of Team 1. / Our team has four members: / | me, / Bora, / Raksa, / and Mengkuang.",
        cap_kh="ក្រុមទី ១\nបញ្ញា · បូរ៉ា · រក្សា · ម៉េងគ័ង",
        cap_en="Team 1\nPanhna · Bora · Raksa · Mengkuang",
        visual=("Four real team photos appear side by side in simple frames on the off-white background. "
                "Each name is under its photo. When the narrator says a name, that photo becomes fully bright "
                "and the others stay slightly faded."),
        prompt=None,
        audio="Music cue A. One very soft click as each photo appears (optional).",
        trans="Photos slide out to the left; SC-004 text slides in (0.4 s).",
        edit=("Use real, recent photos with the same crop and background if possible. "
              "Keyframe opacity 60% → 100% for each name, timed to the voice-over."),
        asset="2D motion graphics + real team photos",
        src="SC-003-team-photos/ (4 images)",
    ),
    dict(
        id="SC-004", ch=1, title="Project and supervisor", dur=11,
        kh=("ថ្ងៃនេះ / ពួកយើងសូមធ្វើបទបង្ហាញអំពីគម្រោងសិក្សា / | ក្រោមការណែនាំរបស់លោកគ្រូ កែវ តុងហេង។ // | "
            "គម្រោងនេះមានឈ្មោះថា / AI Chatbot Management System (Telegram Bot)។"),
        en=("Today, / we will present our study project, / | supervised by Lecturer Keo Tongheng. // | "
            "It is called / the AI Chatbot Management System (Telegram Bot)."),
        cap_kh="ក្រោមការណែនាំ៖ លោកគ្រូ កែវ តុងហេង\nAI Chatbot Management System (Telegram Bot)",
        cap_en="Supervisor: Lecturer Keo Tongheng\nAI Chatbot Management System (Telegram Bot)",
        visual=("A clean text card. First line: the supervisor's name. Then the project name appears larger in "
                "the centre. No photo of the lecturer is needed."),
        prompt=None,
        audio="Music cue A, slowly building.",
        trans="Cross-dissolve (0.5 s) into SC-005.",
        edit="Check the spelling of the lecturer's name in both languages with your faculty before export.",
        asset="2D motion graphics",
        src="—",
    ),
    dict(
        id="SC-005", ch=1, title="Purpose and welcome", dur=10,
        kh=("គម្រោងនេះ ជួយឆ្លើយសំណួរដែលនិស្សិតសួរញឹកញាប់ បានភ្លាមៗ / ទោះជាពេលយប់ក៏ដោយ / | "
            "ហើយជួយសម្រាលការងាររបស់បុគ្គលិក។ // | សូមរីករាយទស្សនាទាំងអស់គ្នា។"),
        en=("This system answers students' frequent questions right away, / even at night, / | "
            "and it reduces the workload of staff. // | We hope you enjoy our presentation."),
        cap_kh="ឆ្លើយភ្លាមៗ · សម្រាលការងារបុគ្គលិក",
        cap_en="Instant answers · Less repeated work",
        visual=("A simple three-step line diagram draws from left to right: "
                "(1) a student's question → (2) the bot answers from saved FAQs → (3) staff handle the questions "
                "the bot cannot answer. Thin dark lines, one muted accent colour."),
        prompt=None,
        audio="Music cue A ends softly at the end of the scene.",
        trans="Dip to black (0.8 s) — the story begins.",
        edit="Draw each step with a 'wipe' or 'line draw' animation, 0.6 s each, timed to the voice.",
        asset="2D motion graphics",
        src="—",
    ),

    # ---------------- Chapter 2 — The Problem ----------------
    dict(
        id="SC-006", ch=2, title="Meet Sokha", dur=8,
        kh="នេះគឺ សុខា។ / នាងចង់ដាក់ពាក្យចូលសិក្សា នៅសាកលវិទ្យាល័យមួយ / | ប៉ុន្តែនាងមិនដឹងថា ត្រូវការឯកសារអ្វីខ្លះទេ។",
        en="This is Sokha. / She wants to apply to a university, / | but she does not know which documents she needs.",
        cap_kh="សុខា · អ្នកដាក់ពាក្យចូលសិក្សា (តួអង្គប្រឌិត)",
        cap_en="Sokha · University applicant (fictional character)",
        visual=("Evening in Sokha's bedroom. She sits at her desk and looks through a folder of papers. "
                "She stops, looks unsure, and touches her chin. Her name appears as a small lower-third."),
        prompt=("Medium shot, slow dolly-in. {SOKHA} Setting: {HOME_NIGHT} She sits at the desk and slowly turns "
                "the pages of a beige document folder with blank printed pages. She stops, looks a little unsure, "
                "and lightly touches her chin. Warm lamp light on her face, cool blue light from the window. "
                "Quiet, thoughtful mood."),
        audio="Music cue B starts: slow, soft piano. Room tone; soft page-turn sound.",
        trans="Straight cut to SC-007.",
        edit="Lower-third on for 3 s. 'Fictional character' in smaller grey text under the name.",
        asset="AI-generated video",
        src="SC-006-AI.mp4",
    ),
    dict(
        id="SC-007", ch=2, title="Midnight message", dur=8,
        kh="នាងផ្ញើសារ / ដើម្បីសួរអំពីនីតិវិធីដាក់ពាក្យ / | និងឯកសារដែលត្រូវការ។",
        en="She sends a message / to ask about the application process / | and the required documents.",
        cap_kh="00:12",
        cap_en="00:12",
        visual=("Close-up over Sokha's shoulder: she types on her phone. Cut to a full-screen, simple chat "
                "mock-up (not Telegram, because the bot does not exist yet) with her message: "
                "'ជម្រាបសួរ! ខ្ញុំចង់ដាក់ពាក្យចូលរៀន។ តើត្រូវការឯកសារអ្វីខ្លះ?' "
                "(English version: 'Hello! I want to apply. Which documents do I need?'). A small clock shows 00:12."),
        prompt=("Over-the-shoulder close-up. {SOKHA} Setting: {HOME_NIGHT} She holds her phone with both hands and "
                "types a message with her thumbs. The phone screen is a plain, flat green colour for easy screen "
                "replacement. The lamp is the only warm light; the room is dark around her. Slow, gentle push-in. "
                "Quiet, late-night mood."),
        audio="Music cue B. Soft phone typing sounds, then a short 'message sent' sound.",
        trans="Match cut from the phone to the full-screen chat mock-up.",
        edit=("Replace the green phone screen with the mock-up (CapCut: Chroma key; DaVinci: Qualifier or 3D keyer). "
              "If the green screen is not clean, cut to the full-screen mock-up instead."),
        asset="AI-generated video + 2D chat mock-up",
        src="SC-007-AI.mp4, SC-007-mockup-KH.png, SC-007-mockup-EN.png",
    ),
    dict(
        id="SC-008", ch=2, title="No reply at midnight", dur=6,
        kh="ប៉ុន្តែពេលនោះ ជាពាក់កណ្ដាលអធ្រាត្រទៅហើយ។ / | គ្មាននរណាឆ្លើយតបមកវិញទេ។",
        en="But it is already midnight. / | Nobody replies.",
        cap_kh="គ្មានចម្លើយ",
        cap_en="No reply",
        visual=("Sokha waits and looks at her phone. The screen light is on her face. She sighs softly and puts "
                "the phone face-down on the desk. A small clock overlay moves from 00:12 to 00:45. "
                "The message shows 'sent' but no reply."),
        prompt=("Medium close-up, static camera. {SOKHA} Setting: {HOME_NIGHT} She looks at her phone and waits. "
                "Soft phone light on her face. After a moment she sighs quietly and places the phone face-down on "
                "the desk. Subtle disappointment, not dramatic. Dim, quiet night atmosphere."),
        audio="Music cue B. A quiet clock tick for 2 seconds, then silence under the last line.",
        trans="Slow fade to white-ish morning light (0.8 s) into SC-009.",
        edit="Animate the clock overlay with two keyframes (00:12 → 00:45). Keep it small, top-right.",
        asset="AI-generated video + small clock overlay",
        src="SC-008-AI.mp4",
    ),
    dict(
        id="SC-009", ch=2, title="Meet Dara", dur=6,
        kh="នេះគឺ ដារ៉ា។ / | គាត់ជាបុគ្គលិកផ្នែកបម្រើសេវាអតិថិជន នៅសាកលវិទ្យាល័យ។",
        en="This is Dara. / | He works in customer service at the university.",
        cap_kh="ដារ៉ា · បុគ្គលិកបម្រើសេវាអតិថិជន (តួអង្គប្រឌិត)",
        cap_en="Dara · Customer service staff (fictional character)",
        visual=("Morning. Dara walks into the help-desk office with a coffee cup, sits at his desk, and opens "
                "his laptop. His name appears as a lower-third."),
        prompt=("Medium-wide shot, slow pan following the subject. {DARA} Setting: {OFFICE} He walks in holding a "
                "white coffee cup, puts it on the desk, sits down and opens his laptop. The laptop screen is a "
                "plain, flat green colour. Bright, fresh morning light. Calm, ordinary workday mood."),
        audio="Music cue B lighter. Office ambience, soft footsteps, laptop opening.",
        trans="Straight cut to SC-010.",
        edit="Same lower-third style as SC-006.",
        asset="AI-generated video",
        src="SC-009-AI.mp4",
    ),
    dict(
        id="SC-010", ch=2, title="A full inbox", dur=8,
        kh=("ព្រឹកឡើង ពេលគាត់មកដល់កន្លែងធ្វើការ / គាត់ឃើញសារជាច្រើនកំពុងរង់ចាំ / | "
            "ហើយភាគច្រើន ជាសំណួរដដែលៗ។"),
        en=("In the morning, when he arrives at work, / he finds many messages waiting. / | "
            "Most of them are the same questions again and again."),
        cap_kh="សំណួរដដែលៗ",
        cap_en="The same questions again and again",
        visual=("Dara's eyebrows rise a little. Cut to a simple inbox mock-up that fills with many rows. "
                "Many rows ask the same thing ('Which documents do I need?', 'តើត្រូវការឯកសារអ្វីខ្លះ?', "
                "'When is the deadline?'). The repeated rows get the same light-grey tint. Sokha's message is one "
                "of them."),
        prompt=("Close-up, static camera, slight push-in. {DARA} Setting: {OFFICE} He looks at his laptop screen "
                "(screen not visible to the camera). His eyebrows rise a little, then he breathes out slowly. "
                "Soft morning light. Realistic, mild surprise."),
        audio="Music cue B. A soft notification sound for each new row (quick, low volume, not annoying).",
        trans="Straight cut to SC-011.",
        edit="Do not show a specific number of messages — it is a story scene, not a statistic.",
        asset="AI-generated video + 2D inbox mock-up",
        src="SC-010-AI.mp4, SC-010-inbox-mockup.mp4",
    ),
    dict(
        id="SC-011", ch=2, title="Answering by hand", dur=6,
        kh="គាត់ចាប់ផ្ដើមឆ្លើយសារទាំងនោះ / | ម្ដងមួយៗ ដោយដៃ។",
        en="He starts answering them / | one by one, by hand.",
        cap_kh="ឆ្លើយម្ដងមួយៗ",
        cap_en="One by one",
        visual=("Quick, calm cuts: Dara types, copies a reply from a notes file, pastes it, and sends it. "
                "A simple overlay shows the same reply text pasted three times."),
        prompt=("Close-up of hands on a laptop keyboard and trackpad, then a side close-up of his face. {DARA} "
                "Setting: {OFFICE} He types, copies and pastes in a steady, repeated rhythm. The screen is not "
                "visible or is a plain green colour. Natural daylight. Routine, slightly tired mood."),
        audio="Music cue B. Keyboard typing and trackpad clicks.",
        trans="Straight cut to SC-012.",
        edit="Three short cuts of about 2 s each to show repetition.",
        asset="AI-generated video + simple text overlay",
        src="SC-011-AI.mp4",
    ),
    dict(
        id="SC-012", ch=2, title="Tired", dur=5,
        kh="វាចំណាយពេលយូរ / | ហើយគួរឱ្យធុញទ្រាន់ណាស់។",
        en="It takes a long time, / | and it is very tiring.",
        cap_kh="",
        cap_en="",
        visual="Dara leans back in his chair, takes off his glasses for a second, and rubs his eyes. Tired, but calm.",
        prompt=("Medium shot, static camera. {DARA} Setting: {OFFICE}, now late morning. He leans back in his "
                "chair, takes off his glasses for a moment and gently rubs his eyes, then puts the glasses back on. "
                "Natural, believable tiredness, not dramatic."),
        audio="Music cue B. A soft breath. Office ambience.",
        trans="Straight cut to SC-013.",
        edit="Hold the shot; no overlay text.",
        asset="AI-generated video",
        src="SC-012-AI.mp4",
    ),
    dict(
        id="SC-013", ch=2, title="The wish", dur=8,
        kh="គាត់គិតថា៖ / បើមានកម្មវិធីមួយ ដែលអាចជួយឆ្លើយសំណួរដដែលៗទាំងនេះ / | ច្បាស់ជាល្អណាស់។",
        en="He thinks: / “If only a program / | could answer these repeated questions for me.”",
        cap_kh="",
        cap_en="",
        visual=("Dara looks out of the window, thinking. A small hand-drawn thought bubble appears next to him "
                "(thin dark line). Inside it, a question mark slowly changes into a check mark."),
        prompt=("Medium close-up, slow push-in. {DARA} Setting: {OFFICE} He turns his head and looks out of the "
                "large window, thinking quietly. Soft daylight on his face. Hopeful, thoughtful mood."),
        audio="Music cue B fades out. A short, soft rising tone as the check mark appears.",
        trans="Soft cross-dissolve (0.6 s) into SC-014 — the solution.",
        edit="Draw the thought bubble in your editor (shape + line animation), not with AI.",
        asset="AI-generated video + 2D line drawing",
        src="SC-013-AI.mp4",
    ),

    # ---------------- Chapter 3 — Our Solution ----------------
    dict(
        id="SC-014", ch=3, title="Our solution", dur=12,
        kh=("ដូច្នេះ / ពួកយើងបានបង្កើត AI Chatbot Management System (Telegram Bot)។ // | "
            "វាមានពីរផ្នែក៖ / Telegram Bot សម្រាប់និស្សិត / | និងផ្ទាំងគ្រប់គ្រង (Dashboard) លើវេបសាយ សម្រាប់បុគ្គលិក។"),
        en=("So, / we built the AI Chatbot Management System (Telegram Bot). // | "
            "It has two parts: / a Telegram bot for students, / | and a web dashboard for staff."),
        cap_kh="Telegram Bot សម្រាប់និស្សិត · Dashboard សម្រាប់បុគ្គលិក",
        cap_en="Telegram bot for students · Web dashboard for staff",
        visual=("The project name appears. Then a simple diagram: on the left, a phone frame with a real Telegram "
                "screenshot of the bot; on the right, a laptop frame with the real dashboard screenshot "
                "(docs/screenshots/dashboard.png). A thin line connects both to a small database shape in the middle."),
        prompt=None,
        audio="Music cue C starts: light, steady, optimistic.",
        trans="Zoom into the laptop frame → SC-015.",
        edit=("Use real screenshots only. Device frames: simple, flat, light grey. "
              "Diagram based on docs/architecture.md (Telegram user → bot → database ← admin dashboard)."),
        asset="2D motion graphics + real screenshots",
        src="SC-014-diagram.mp4, docs/screenshots/dashboard.png",
    ),
    dict(
        id="SC-015", ch=3, title="Managing FAQs", dur=8,
        kh="តាមរយៈផ្ទាំងគ្រប់គ្រង / បុគ្គលិកអាចបង្កើត គ្រប់គ្រង / | និងរក្សាទុកសំណួរដែលគេសួរញឹកញាប់ (FAQ)។",
        en="In the dashboard, / staff can create, manage, / | and save frequently asked questions, or FAQs.",
        cap_kh="FAQ · បង្កើត · គ្រប់គ្រង · រក្សាទុក",
        cap_en="FAQ · Create · Manage · Save",
        visual=("Real recording of the FAQ page: the 'Add FAQ' form (Question, Answer, Category, Language, "
                "Keywords, Priority), then the FAQ table with Disable/Enable buttons. A thin outline highlights "
                "each part as it is mentioned."),
        prompt=None,
        audio="Music cue C (lower). Soft mouse clicks.",
        trans="Cut to SC-016.",
        edit=("Show only what exists: Add FAQ, Disable/Enable, Delete. There is no text 'Edit' button in the "
              "current code — see the checklist."),
        asset="Dashboard screen recording + highlight boxes",
        src="SC-015-DB.mp4",
    ),
    dict(
        id="SC-016", ch=3, title="Khmer and English", dur=6,
        kh="Bot អាចឆ្លើយសំណួរ / | ទាំងជាភាសាខ្មែរ និងភាសាអង់គ្លេស។",
        en="The bot can handle questions / | in both Khmer and English.",
        cap_kh="ខ្មែរ · English",
        cap_en="Khmer · English",
        visual=("Split screen: two phone recordings side by side. Left: the Khmer welcome message and menu. "
                "Right: the English welcome message and menu."),
        prompt=None,
        audio="Music cue C.",
        trans="Cut to SC-017.",
        edit="Record both phones with the same theme (light mode) and the same font size.",
        asset="Telegram screen recordings (split screen)",
        src="SC-016-TG-KH.mp4, SC-016-TG-EN.mp4",
    ),
    dict(
        id="SC-017", ch=3, title="Different words, same meaning", dur=7,
        kh="វាអាចយល់សំណួរដែលមានន័យដូចគ្នា / | ទោះបីជាប្រើពាក្យខុសគ្នាក៏ដោយ។",
        en="It can understand questions with the same meaning, / | even when they use different words.",
        cap_kh="ពាក្យខុសគ្នា · ន័យដូចគ្នា",
        cap_en="Different words · Same meaning",
        visual=("Motion graphic: two question cards with different wording move into one answer card. "
                "Khmer version: 'តើខ្ញុំត្រូវការឯកសារអ្វីខ្លះដើម្បីចុះឈ្មោះ?' and 'តើចុះឈ្មោះចូលរៀន ត្រូវការឯកសារអ្វីខ្លះ?'. "
                "English version: 'What documents do I need to register?' and "
                "'What are the required documents for registration?'. Both point to the same saved answer."),
        prompt=None,
        audio="Music cue C. A soft 'join' sound when the cards meet.",
        trans="Cut to SC-018.",
        edit="Make two versions of this graphic (KH and EN). Keep card positions the same in both.",
        asset="2D motion graphics",
        src="SC-017-MG-KH.mp4, SC-017-MG-EN.mp4",
    ),
    dict(
        id="SC-018", ch=3, title="Honest when it does not know", dur=10,
        kh=("បើវាជួបសំណួរដែលមិនអាចឆ្លើយបាន / វានឹងប្រាប់ដោយត្រង់ៗ ថាវាមិនដឹង / | "
            "ហើយបញ្ជូនការសន្ទនាបន្ត ទៅកាន់មនុស្ស។"),
        en=("If it cannot answer a question, / it says so honestly, / | "
            "and passes the conversation to a human."),
        cap_kh="មិនទាយ · បញ្ជូនទៅមនុស្ស",
        cap_en="No guessing · Human support",
        visual=("Simple flow: question → 'no reliable answer found' → the real fallback message with three "
                "buttons (Rephrase · Main Menu · Human Support) → a line to a person outline at the dashboard."),
        prompt=None,
        audio="Music cue C.",
        trans="Cut to SC-019.",
        edit="Use a real screenshot of the fallback message (record it in SC-028 and reuse a frame).",
        asset="2D motion graphics + real screenshot",
        src="SC-018-MG.mp4",
    ),
    dict(
        id="SC-019", ch=3, title="Good for both sides", dur=9,
        kh="ដូច្នេះ / និស្សិតទទួលបានចម្លើយភ្លាមៗ / | ហើយបុគ្គលិកមិនចាំបាច់ឆ្លើយសំណួរដដែលៗទៀតទេ។",
        en="So, / students get answers right away, / | and staff no longer need to answer the same questions again and again.",
        cap_kh="និស្សិត៖ ចម្លើយភ្លាមៗ · បុគ្គលិក៖ ការងារដដែលៗតិចជាងមុន",
        cap_en="Students: instant answers · Staff: less repeated work",
        visual=("Split screen. Left: Sokha at night, smiling a little at her phone. "
                "Right: Dara in the morning, relaxed, calmly looking at his laptop."),
        prompt=("Two separate clips for a split screen. Clip 1 — medium close-up, static. {SOKHA} Setting: "
                "{HOME_NIGHT} She looks at her phone and smiles a little, relieved. Clip 2 — medium shot, slow "
                "push-in. {DARA} Setting: {OFFICE} He sits back comfortably, sips coffee, and calmly looks at his "
                "laptop (screen not visible). Both clips: warm, positive, natural."),
        audio="Music cue C rises slightly.",
        trans="Wipe from left to right into SC-020.",
        edit="Crop each clip to 50% width; keep faces in the centre of each half.",
        asset="AI-generated video (2 clips, split screen)",
        src="SC-019-AI-sokha.mp4, SC-019-AI-dara.mp4",
    ),

    # ---------------- Chapter 4 — Student Experience ----------------
    dict(
        id="SC-020", ch=4, title="/start and Khmer", dur=8,
        kh="សុខាចាប់ផ្ដើមប្រើ / ដោយផ្ញើ /start / | ហើយជ្រើសរើសភាសាខ្មែរ។",
        en="Sokha starts / by sending /start, / | and she chooses Khmer.",
        cap_kh="/start → ខ្មែរ",
        cap_en="/start → Khmer",
        visual=("2 s: Sokha at night picks up her phone (same bedroom). Then the real Telegram recording: she sends "
                "/start, the bot asks 'Please choose your language' with two buttons (English · ខ្មែរ), she taps "
                "ខ្មែរ, and the Khmer welcome message and menu appear."),
        prompt=("Medium close-up, static camera. {SOKHA} Setting: {HOME_NIGHT} She picks up her phone from the "
                "desk and starts typing, looking focused and a little hopeful. Phone screen is a plain green colour."),
        audio="Music cue C (low). Soft tap sounds.",
        trans="Cut from AI shot to phone recording.",
        edit=("Use a test Telegram account named 'Sokha' (for example 'Sok Sokha'). Start from a new account, so "
              "the bot asks for the language. Show the phone recording in a simple phone frame, centred."),
        asset="AI-generated video (2 s) + Telegram screen recording",
        src="SC-020-AI.mp4, SC-020-TG.mp4",
    ),
    dict(
        id="SC-021", ch=4, title="The same question, again", dur=7,
        kh="នាងសួរសំណួរដដែល / | ដែលនាងបានសួរកាលពីយប់មិញ។",
        en="She asks the same question / | she asked last night.",
        cap_kh="តើចុះឈ្មោះចូលរៀន ត្រូវការឯកសារអ្វីខ្លះ?",
        cap_en="Which documents does she need?",
        visual="Telegram recording: Sokha types 'តើចុះឈ្មោះចូលរៀន ត្រូវការឯកសារអ្វីខ្លះ?' and sends it.",
        prompt=None,
        audio="Typing sound, 'sent' sound.",
        trans="Continuous recording into SC-022.",
        edit="Type at a slow, readable speed, or speed up the typing 2× in the editor.",
        asset="Telegram screen recording",
        src="SC-021-TG.mp4",
    ),
    dict(
        id="SC-022", ch=4, title="Instant answer", dur=6,
        kh="Bot ឆ្លើយភ្លាមៗ / | ដោយប្រើចម្លើយពី FAQ ដែលមានស្រាប់។",
        en="The bot answers immediately, / | using an answer from the existing FAQ.",
        cap_kh="ចម្លើយពី FAQ",
        cap_en="Answer from the FAQ",
        visual=("The bot's answer appears at once, with 👍 and 👎 buttons under it. "
                "A small clock overlay still shows 00:12 — the same time she got no reply before."),
        prompt=None,
        audio="Soft 'message received' sound. Music cue C.",
        trans="Continuous recording into SC-023.",
        edit="Highlight the answer bubble with a thin outline for 1.5 s.",
        asset="Telegram screen recording + clock overlay",
        src="SC-022-TG.mp4",
    ),
    dict(
        id="SC-023", ch=4, title="Feedback 👍", dur=5,
        kh="នាងចុច 👍 / | ដើម្បីផ្ដល់មតិកែលម្អ។",
        en="She taps 👍 / | to give feedback.",
        cap_kh="👍 មតិកែលម្អ",
        cap_en="👍 Feedback",
        visual="Sokha taps 👍. The buttons disappear and a short 'Thank you for your feedback!' message appears at the top.",
        prompt=None,
        audio="Tap sound.",
        trans="Cut to SC-024.",
        edit="Add a small, soft tap circle where she taps (no glow).",
        asset="Telegram screen recording",
        src="SC-023-TG.mp4",
    ),
    dict(
        id="SC-024", ch=4, title="Switch to English", dur=5,
        kh="នាងក៏អាចប្ដូរ / | ទៅភាសាអង់គ្លេសបានដែរ។",
        en="She can also switch / | to English.",
        cap_kh="🌐 ភាសា → English",
        cap_en="🌐 Language → English",
        visual="She taps '🌐 ភាសា' in the menu, then 'English'. The English welcome message and menu appear.",
        prompt=None,
        audio="Tap sounds.",
        trans="Continuous recording into SC-025.",
        edit="Speed up waiting time if needed (no more than 2×).",
        asset="Telegram screen recording",
        src="SC-024-TG.mp4",
    ),
    dict(
        id="SC-025", ch=4, title="Different words, still understood", dur=10,
        kh=("នាងសួរសំណួរដដែល ប៉ុន្តែប្រើពាក្យផ្សេង។ / | "
            "Bot នៅតែយល់ / ទោះពាក្យខុសពីអ្វីដែលបានរក្សាទុកក៏ដោយ។"),
        en=("She asks the same question in different words. / | "
            "The bot still understands, / even though the words are not the same as the saved question."),
        cap_kh="បានរក្សាទុក៖ What documents do I need to register?\nបានសួរ៖ What are the required documents for registration?",
        cap_en="Saved: What documents do I need to register?\nAsked: What are the required documents for registration?",
        visual=("She types 'What are the required documents for registration?'. The bot answers: "
                "'Bring your ID card or passport, one photo (4x6), and your latest certificate.' "
                "A small comparison card shows the saved question and the new question."),
        prompt=None,
        audio="Typing and received sounds.",
        trans="Continuous recording into SC-026.",
        edit="Rehearse this exact sentence before recording. If it does not match, see the checklist.",
        asset="Telegram screen recording + comparison card",
        src="SC-025-TG.mp4",
    ),
    dict(
        id="SC-026", ch=4, title="Capturing a date", dur=10,
        kh="វាថែមទាំងអាចចាប់យក / និងរក្សាទុកកាលបរិច្ឆេទ / | ក្នុងការសន្ទនាបានទៀតផង។",
        en="It can even find a date / in the conversation / | and save it.",
        cap_kh="កាលបរិច្ឆេទ៖ 2026-12-15 · បានរក្សាទុក",
        cap_en="Date: 2026-12-15 · Saved",
        visual=("She types 'I want to book an appointment on 2026-12-15'. The bot replies: 'Thank you! We noted "
                "your appointment request for 2026-12-15. Our team will confirm it soon…'. The date is highlighted "
                "in both messages."),
        prompt=None,
        audio="Typing and received sounds.",
        trans="Cut to SC-027.",
        edit=("Choose a date that is still in the future on the day you show the video. "
              "The same date appears later in the dashboard (SC-033), so keep it the same."),
        asset="Telegram screen recording + highlight",
        src="SC-026-TG.mp4",
    ),
    dict(
        id="SC-027", ch=4, title="A question the bot does not know", dur=6,
        kh="បន្ទាប់មក / | នាងសួរសំណួរមួយ ដែល Bot មិនដឹងចម្លើយ។",
        en="Next, / | she asks a question the bot does not know.",
        cap_kh="Is there a bus to campus?",
        cap_en="Is there a bus to campus?",
        visual="She types 'Is there a bus to campus?' and sends it.",
        prompt=None,
        audio="Typing sound.",
        trans="Continuous recording into SC-028.",
        edit="This question has no FAQ in the demo data (checked by the team's demo script).",
        asset="Telegram screen recording",
        src="SC-027-TG.mp4",
    ),
    dict(
        id="SC-028", ch=4, title="No guessing", dur=8,
        kh="Bot មិនទាយចម្លើយទេ។ / | វាសុំទោស / ហើយផ្ដល់ជម្រើសជំនួយ។",
        en="The bot does not guess. / | It says sorry, / and offers help options.",
        cap_kh="សរសេរម្ដងទៀត · ម៉ឺនុយមេ · ជំនួយពីមនុស្ស",
        cap_en="Rephrase · Main Menu · Human Support",
        visual=("The bot replies: 'Sorry, I did not understand your question. Please rephrase it, open the menu, "
                "or ask for human support.' Three buttons appear under it: Rephrase · Main Menu · Human Support."),
        prompt=None,
        audio="Received sound. Music cue C, slightly softer.",
        trans="Continuous recording into SC-029.",
        edit="Outline the three buttons one by one (0.4 s each).",
        asset="Telegram screen recording + highlight",
        src="SC-028-TG.mp4",
    ),
    dict(
        id="SC-029", ch=4, title="Asking for a human", dur=9,
        kh="នាងជ្រើសរើស ជំនួយពីមនុស្ស។ // | ចុចតែម្ដង / សំណើរបស់នាងត្រូវបានផ្ញើទៅក្រុមជំនួយ។",
        en="She chooses Human Support. // | With just one tap, / her request goes to the support team.",
        cap_kh="សំណើត្រូវបានផ្ញើទៅក្រុមជំនួយ",
        cap_en="Request sent to the support team",
        visual=("She taps 'Human Support'. The bot replies: 'Your request was sent to our support team. "
                "An agent will reply here soon.' Then 2 s AI shot: Sokha puts her phone down, relieved, and "
                "switches off the lamp."),
        prompt=("Medium shot, static camera. {SOKHA} Setting: {HOME_NIGHT} She puts her phone on the desk, smiles "
                "a little with relief, and switches off the desk lamp. The room becomes dark blue. Peaceful mood."),
        audio="Tap, received sound. Music cue C resolves softly.",
        trans="Dip to black (0.6 s) — next morning.",
        edit="End of Chapter 4.",
        asset="Telegram screen recording + AI-generated video (2 s)",
        src="SC-029-TG.mp4, SC-029-AI.mp4",
    ),

    # ---------------- Chapter 5 — Administrator Experience ----------------
    dict(
        id="SC-030", ch=5, title="Next morning: login", dur=6,
        kh="ព្រឹកបន្ទាប់ / | ដារ៉ាចូលទៅក្នុងប្រព័ន្ធ។",
        en="The next morning, / | Dara logs in to the system.",
        cap_kh="ព្រឹកបន្ទាប់",
        cap_en="The next morning",
        visual=("2–3 s AI shot: Dara sits down and opens his laptop (same office, same clothes). "
                "Then the real login page: email (blurred) and password (dots), click Log in."),
        prompt=("Medium shot, slow push-in. {DARA} Setting: {OFFICE} He sits down at his desk, opens the laptop and "
                "starts typing, focused and relaxed. Laptop screen is a plain green colour. Fresh morning light."),
        audio="Music cue C (new section, light). Office ambience, keyboard.",
        trans="Cut from AI shot to the dashboard recording.",
        edit="Blur the email address. Never show a real password.",
        asset="AI-generated video + dashboard screen recording",
        src="SC-030-AI.mp4, SC-030-DB.mp4",
    ),
    dict(
        id="SC-031", ch=5, title="Statistics and unanswered questions", dur=8,
        kh="គាត់ឃើញស្ថិតិ / | និងសំណួរដែល Bot មិនអាចឆ្លើយបាន។",
        en="He sees the statistics / | and the questions the bot could not answer.",
        cap_kh="ស្ថិតិ · សំណួរដែលមិនទាន់មានចម្លើយ",
        cap_en="Statistics · Unanswered questions",
        visual=("Real dashboard: statistic cards, KPIs and charts. Slow scroll down to 'Top unanswered questions', "
                "where 'is there a bus to campus' is in the list."),
        prompt=None,
        audio="Music cue C (low). Soft scroll sound (optional).",
        trans="Cut to SC-032.",
        edit="Highlight Sokha's question in the list with a thin outline.",
        asset="Dashboard screen recording + highlight",
        src="SC-031-DB.mp4",
    ),
    dict(
        id="SC-032", ch=5, title="Sokha's request in the queue", dur=6,
        kh="សំណើរបស់សុខា / | កំពុងរង់ចាំក្នុងជួររបស់គាត់រួចហើយ។",
        en="Sokha's request / | is already waiting in his queue.",
        cap_kh="ជួររង់ចាំជំនួយ",
        cap_en="Support queue",
        visual="He clicks 'Conversations' (with the number of open requests). Sokha's request is in the support queue.",
        prompt=None,
        audio="Click sound.",
        trans="Click → SC-033.",
        edit="Highlight the small number next to 'Conversations', then Sokha's row.",
        asset="Dashboard screen recording + highlight",
        src="SC-032-DB.mp4",
    ),
    dict(
        id="SC-033", ch=5, title="The whole conversation", dur=8,
        kh="គាត់អាចមើលការសន្ទនាទាំងមូល / | រវាងសុខា និង Bot នៅទីនេះ។",
        en="Here, he can read the whole conversation / | between Sokha and the bot.",
        cap_kh="ការសន្ទនាទាំងមូល",
        cap_en="The whole conversation",
        visual=("He opens the conversation. The timeline shows every message: the Khmer question and answer, the "
                "English question, the appointment date, the bus question, and the support request. The 'Detected' "
                "box shows the saved date 2026-12-15."),
        prompt=None,
        audio="Music cue C.",
        trans="Cut to SC-034.",
        edit="Slow scroll. Briefly highlight the 'Detected' date to connect with SC-026.",
        asset="Dashboard screen recording + highlight",
        src="SC-033-DB.mp4",
    ),
    dict(
        id="SC-034", ch=5, title="Reply to Telegram", dur=8,
        kh="គាត់សរសេរចម្លើយ / | ហើយចម្លើយនោះ ទៅដល់ Telegram ក្នុងទូរស័ព្ទរបស់សុខា។",
        en="He types a reply, / | and it arrives in Telegram on Sokha's phone.",
        cap_kh="ឆ្លើយពី Dashboard → Telegram",
        cap_en="Reply from the dashboard → Telegram",
        visual=("He types in 'Reply to the user in Telegram' and clicks 'Send reply'. Split screen: "
                "a second later the message appears on Sokha's phone."),
        prompt=None,
        audio="Typing, click, then 'message received' sound on the phone side.",
        trans="Cut to SC-035.",
        edit=("Record the dashboard and the phone at the same time. Sync them with the moment you click "
              "'Send reply'. Write a true answer about transport (ask the university first)."),
        asset="Dashboard + Telegram screen recordings (split screen)",
        src="SC-034-DB.mp4, SC-034-TG.mp4",
    ),
    dict(
        id="SC-035", ch=5, title="Marked as Resolved", dur=6,
        kh="បន្ទាប់មក / | គាត់កំណត់សំណើនេះថា បានដោះស្រាយ។",
        en="Then, / | he marks the request as Resolved.",
        cap_kh="→ Resolved (បានដោះស្រាយ)",
        cap_en="→ Resolved",
        visual=("He clicks '→ Resolved'. The status changes. On the phone, Sokha receives: 'Your support request "
                "was marked as resolved…'."),
        prompt=None,
        audio="Click sound, soft received sound.",
        trans="Cut back to the dashboard home → SC-036.",
        edit="Small split screen or quick cut to the phone for 1.5 s.",
        asset="Dashboard + Telegram screen recordings",
        src="SC-035-DB.mp4, SC-035-TG.mp4",
    ),
    dict(
        id="SC-036", ch=5, title="Add FAQ — question filled in", dur=9,
        kh="ដារ៉ាចុច Add FAQ។ / | សំណួររបស់សុខា / ត្រូវបានបំពេញរួចដោយស្វ័យប្រវត្តិ។",
        en="Dara clicks Add FAQ. / | Sokha's question / is already filled in automatically.",
        cap_kh="Add FAQ · សំណួរបំពេញស្វ័យប្រវត្តិ",
        cap_en="Add FAQ · Question filled in automatically",
        visual=("Back on the dashboard, in 'Top unanswered questions', he clicks 'Add FAQ' next to "
                "'is there a bus to campus'. The FAQ page opens and the Question field already contains it."),
        prompt=None,
        audio="Click sound.",
        trans="Continuous recording into SC-037.",
        edit=("Highlight the filled Question field. The saved question is in lower case without '?'. "
              "He may tidy it to 'Is there a bus to campus?' — that is fine."),
        asset="Dashboard screen recording + highlight",
        src="SC-036-DB.mp4",
    ),
    dict(
        id="SC-037", ch=5, title="Type the answer and save", dur=6,
        kh="គាត់គ្រាន់តែបញ្ចូលចម្លើយ / ដោយមិនចាំបាច់វាយសំណួរឡើងវិញ / | ហើយរក្សាទុក។",
        en="He only types the answer, / with no need to type the question again, / | and saves it.",
        cap_kh="បញ្ចូលចម្លើយ → រក្សាទុក",
        cap_en="Type the answer → Save",
        visual=("He types the answer, chooses a category and language, adds keywords "
                "'bus to campus, shuttle bus, campus bus', and clicks 'Add FAQ'. The new row appears in the table."),
        prompt=None,
        audio="Typing, click.",
        trans="Cut to SC-038.",
        edit="Do not use a short keyword like 'bus' — it also matches the word 'business'. Use the phrases above.",
        asset="Dashboard screen recording",
        src="SC-037-DB.mp4",
    ),
    dict(
        id="SC-038", ch=5, title="Another student, different words", dur=8,
        kh="និស្សិតម្នាក់ទៀតសួរសំណួរនោះ ដោយប្រើពាក្យផ្សេង / | ហើយ Bot អាចឆ្លើយបាន។",
        en="Another student asks the same thing in different words, / | and the bot can answer.",
        cap_kh="Is there a shuttle bus to the campus?",
        cap_en="Is there a shuttle bus to the campus?",
        visual=("A second Telegram account (another student) types 'Is there a shuttle bus to the campus?'. "
                "The bot answers with the new FAQ. Optional 1–2 s AI shot: a different student's hands holding a "
                "phone on campus (no face)."),
        prompt=("Optional cutaway. Close-up of a young Cambodian student's hands holding a smartphone with a plain "
                "green screen, sitting on a bench on a modern university campus during the day. Face not visible. "
                "Soft daylight, shallow depth of field. Calm mood."),
        audio="Typing and received sounds.",
        trans="Cut to SC-039.",
        edit="Use a different Telegram account, not Sokha's. Give it a neutral name, for example 'Student B'.",
        asset="Telegram screen recording (+ optional AI cutaway)",
        src="SC-038-TG.mp4, SC-038-AI.mp4 (optional)",
    ),
    dict(
        id="SC-039", ch=5, title="Yesterday unknown, today answered", dur=7,
        kh="សំណួរដែល Bot មិនដឹងកាលពីម្សិលមិញ / | ថ្ងៃនេះ វាឆ្លើយបានហើយ។",
        en="The question the bot could not answer yesterday, / | it can answer today.",
        cap_kh="ម្សិលមិញ៖ មិនមានចម្លើយ → ថ្ងៃនេះ៖ មានចម្លើយ (បុគ្គលិកបានបន្ថែម FAQ)",
        cap_en="Yesterday: no answer → Today: answered (staff added an FAQ)",
        visual=("Two cards side by side: 'Yesterday' with the fallback reply, and 'Today' with the new FAQ answer. "
                "A small line under them: 'A staff member added a verified answer.'"),
        prompt=None,
        audio="Music cue C, a small positive lift.",
        trans="Cut to SC-040.",
        edit="Do not say or show that the AI retrains itself. The knowledge grows because staff add FAQs.",
        asset="2D motion graphics + real screenshots",
        src="SC-039-MG.mp4",
    ),
    dict(
        id="SC-040", ch=5, title="Broadcast", dur=7,
        kh="ដារ៉ាក៏អាចផ្ញើសារ / | ទៅកាន់អ្នកប្រើប្រាស់ Bot ទាំងអស់បានដែរ។",
        en="Dara can also send a message / | to all bot users at once.",
        cap_kh="Broadcast · អ្នកប្រើប្រាស់ទាំងអស់",
        cap_en="Broadcast · All users",
        visual=("Broadcast page: he types a short announcement, chooses 'All users', and the preview shows the "
                "number of recipients. He clicks 'Send / schedule'. The message appears on the phone, and History "
                "shows it was delivered."),
        prompt=None,
        audio="Click, then received sound on the phone.",
        trans="Cut to SC-041.",
        edit="Use a true announcement from the university, or a clearly harmless one for the demo.",
        asset="Dashboard + Telegram screen recordings",
        src="SC-040-DB.mp4, SC-040-TG.mp4",
    ),
    dict(
        id="SC-041", ch=5, title="Report export", dur=7,
        kh="គាត់អាចទាញយករបាយការណ៍ជា PDF ឬ Excel / | ដោយអក្សរខ្មែរបង្ហាញបានត្រឹមត្រូវ។",
        en="He can export reports as PDF or Excel, / | and Khmer text is displayed correctly.",
        cap_kh="Export PDF · Excel · អក្សរខ្មែរត្រឹមត្រូវ",
        cap_en="Export PDF · Excel · Correct Khmer text",
        visual=("Reports page: he picks a date range and clicks 'Export PDF'. The PDF opens; zoom in on a Khmer "
                "question to show the Khmer letters are correct."),
        prompt=None,
        audio="Click sound.",
        trans="Cut to SC-042.",
        edit="Zoom (scale 100% → 150%) on a Khmer line in the PDF. Blur any real personal data.",
        asset="Dashboard screen recording + zoom",
        src="SC-041-DB.mp4",
    ),
    dict(
        id="SC-042", ch=5, title="Account permissions", dur=6,
        kh="គាត់ក៏អាចកំណត់សិទ្ធិប្រើប្រាស់ / | សម្រាប់គណនីផ្សេងៗបានដែរ។",
        en="He can also set the permissions / | for each account.",
        cap_kh="តួនាទី និងសិទ្ធិប្រើប្រាស់",
        cap_en="Roles and permissions",
        visual=("Settings page: 'Roles and permissions' (Administrator, Bot Manager, Content Manager, "
                "Support Agent, Viewer), then 'Admin accounts and agents' with a Viewer account."),
        prompt=None,
        audio="Soft clicks.",
        trans="Cut to SC-043.",
        edit="Blur email addresses.",
        asset="Dashboard screen recording",
        src="SC-042-DB.mp4",
    ),
    dict(
        id="SC-043", ch=5, title="The Viewer role", dur=9,
        kh="គណនី Viewer ឃើញតែឈ្មោះដែលបានបិទបាំង / | ហើយមិនអាចបើក Settings បានទេ។",
        en="A Viewer account only sees masked names, / | and it cannot open Settings.",
        cap_kh="Viewer · ឈ្មោះបិទបាំង · គ្មាន Settings",
        cap_en="Viewer · Masked names · No Settings",
        visual=("He logs out and logs in as the Viewer. The menu has no 'Settings' (and no 'Broadcast'). "
                "On the Users page, names look like 'S** S****' and phone numbers like '012***678'."),
        prompt=None,
        audio="Music cue C ends softly.",
        trans="Dip to black (0.6 s) into Chapter 6.",
        edit="Highlight the menu (where Settings is missing) and one masked name.",
        asset="Dashboard screen recording + highlight",
        src="SC-043-DB.mp4",
    ),

    # ---------------- Chapter 6 — Results and Conclusion ----------------
    dict(
        id="SC-044", ch=6, title="Before and after", dur=9,
        kh=("ឥឡូវនេះ / សុខាទទួលបានចម្លើយ ទោះជាពាក់កណ្ដាលអធ្រាត្រក៏ដោយ / | "
            "ហើយដារ៉ា លែងចម្លងចម្លើយដដែលៗទៀតហើយ។"),
        en=("Now, / Sokha gets answers even at midnight, / | "
            "and Dara no longer copies the same answers again and again."),
        cap_kh="",
        cap_en="",
        visual=("Split screen. Left: Sokha at night reads an answer on her phone and smiles. "
                "Right: Dara, relaxed, helps a visitor at the help desk while the laptop sits beside him."),
        prompt=("Two separate clips for a split screen. Clip 1 — close-up, slow push-in. {SOKHA} Setting: "
                "{HOME_NIGHT} She reads her phone and smiles with relief. Clip 2 — medium shot, static. {DARA} "
                "Setting: {OFFICE} He talks kindly with a student visitor at the counter (visitor seen from behind, "
                "face not visible). Warm, positive, natural."),
        audio="Music cue D starts: warm, uplifting.",
        trans="Cross-dissolve (0.5 s) into SC-045.",
        edit="Same split-screen layout as SC-019, so viewers see the change.",
        asset="AI-generated video (2 clips, split screen)",
        src="SC-044-AI-sokha.mp4, SC-044-AI-dara.mp4",
    ),
    dict(
        id="SC-045", ch=6, title="Test results", dur=13,
        kh=("ក្នុងការសាកល្បងជាមួយសំណួរ ៥៧ ដែលក្រុមយើងបានសរសេរ / | Bot ឆ្លើយត្រូវ ៥៣ សំណួរ / "
            "និងមិនត្រឹមត្រូវ ៤ សំណួរ / | ពោលគឺ ត្រឹមត្រូវប្រហែល ៩២,៩៨ ភាគរយ។"),
        en=("We tested the bot with 57 questions that our team wrote. / | It answered 53 correctly / "
            "and 4 incorrectly. / | That is about 92.98 percent accuracy."),
        cap_kh="សំណួរសាកល្បង ៥៧ · ត្រូវ ៥៣ · មិនត្រូវ ៤ · ≈ ៩២,៩៨%",
        cap_en="57 test questions · 53 correct · 4 incorrect · ≈ 92.98%",
        visual=("Large, clean numbers appear one by one: 57 test questions, 53 correct, 4 incorrect, ≈ 92.98%. "
                "Under them, one horizontal bar: 53 parts in a dark neutral colour, 4 parts in a muted colour. "
                "Small formula: 53 ÷ 57 × 100 ≈ 92.98%."),
        prompt=None,
        audio="Music cue D (low under the voice).",
        trans="Cut to SC-046.",
        edit="Count-up animation for the numbers is fine, but end on the exact values.",
        asset="2D motion graphics",
        src="SC-045-MG-KH.mp4, SC-045-MG-EN.mp4",
    ),
    dict(
        id="SC-046", ch=6, title="What the test means", dur=8,
        kh=("លទ្ធផលនេះ មកពីសំណួរសាកល្បងរបស់ក្រុមយើងផ្ទាល់ / | "
            "មិនមែនមកពីការវាយតម្លៃសាធារណៈទ្រង់ទ្រាយធំទេ។"),
        en=("These results come from our own test questions, / | "
            "not from a large public benchmark."),
        cap_kh="ប្រភព៖ សំណួរសាកល្បងរបស់ក្រុម ៥៧ (អង់គ្លេស ៤២ · ខ្មែរ ១៥)",
        cap_en="Source: our team's 57 test questions (42 English · 15 Khmer)",
        visual="A simple text card with the source of the numbers. Calm, honest, no decoration.",
        prompt=None,
        audio="Music cue D.",
        trans="Cut to SC-047.",
        edit="Source file in the project: docs/evaluation/test_questions.csv (branch feature/all-screens).",
        asset="2D motion graphics",
        src="—",
    ),
    dict(
        id="SC-047", ch=6, title="Next step", dur=8,
        kh="ជំហានបន្ទាប់ / យើងនឹងដាក់ AI Chatbot ឱ្យដំណើរការជាក់ស្ដែង / | ហើយសាកល្បងជាមួយនិស្សិតពិតប្រាកដ។",
        en="Next, / we will deploy the AI chatbot / | and test it with real university students.",
        cap_kh="បន្ទាប់៖ ដាក់ឱ្យដំណើរការ → សាកល្បងជាមួយនិស្សិតពិត",
        cap_en="Next: Deploy → Test with real students",
        visual=("A short line with three points: 'Prototype tested' (done) → 'Deploy' → 'Test with real students'. "
                "Behind it, soft B-roll of students walking on a campus (far away, not recognisable)."),
        prompt=("B-roll. Wide shot of a modern Cambodian university campus during the day. Several students walk "
                "and talk far from the camera, some holding phones; faces are small and not recognisable. "
                "Slow tracking shot. Soft daylight. Hopeful, forward-looking mood."),
        audio="Music cue D builds a little.",
        trans="Cross-dissolve (0.5 s) into SC-048.",
        edit="Put the B-roll at 40% opacity under the roadmap graphic, or blur it slightly.",
        asset="2D motion graphics + AI B-roll",
        src="SC-047-AI-broll.mp4",
    ),
    dict(
        id="SC-048", ch=6, title="Thank you", dur=8,
        kh="ការធ្វើបទបង្ហាញរបស់ពួកយើងត្រូវបានបញ្ចប់។ / | សូមអរគុណលោកគ្រូ និងអ្នកទាំងអស់គ្នា ដែលបានទស្សនា។",
        en="This is the end of our presentation. / | Thank you, Lecturer, and thank you, everyone, for watching.",
        cap_kh="សូមអរគុណ",
        cap_en="Thank you",
        visual="The presenter, Panhna (real footage), says thank you. Or: the four team photos together, with 'Thank you'.",
        prompt=None,
        audio="Music cue D resolves.",
        trans="Fade to the end card.",
        edit="Film this line in the same place as SC-002 for a clean ending.",
        asset="Real camera footage (or team photos) + text",
        src="SC-048-CAM.mp4",
    ),
    dict(
        id="SC-049", ch=6, title="End card", dur=6,
        kh="", en="",
        cap_kh=("ក្រុមទី ១៖ បញ្ញា · បូរ៉ា · រក្សា · ម៉េងគ័ង\nក្រោមការណែនាំ៖ លោកគ្រូ កែវ តុងហេង\n"
                "សាកលវិទ្យាល័យពាណិជ្ជសាស្ត្រ អេស៊ីលីដា\nសុខា និង ដារ៉ា ជាតួអង្គប្រឌិត។"),
        cap_en=("Team 1: Panhna · Bora · Raksa · Mengkuang\nSupervisor: Lecturer Keo Tongheng\n"
                "ACLEDA University of Business\nSokha and Dara are fictional characters."),
        visual="Off-white end card with the credits in the centre. Music fades out.",
        prompt=None,
        audio="Music cue D fades out over 4 s.",
        trans="Fade to black (1 s).",
        edit="Hold for at least 5 s so the credits can be read.",
        asset="2D motion graphics",
        src="—",
    ),
]

CHAPTERS = {
    1: ("Introduction", "សេចក្ដីផ្ដើម"),
    2: ("The Problem", "បញ្ហា"),
    3: ("Our Solution", "ដំណោះស្រាយរបស់យើង"),
    4: ("Student Experience", "បទពិសោធន៍របស់និស្សិត"),
    5: ("Administrator Experience", "បទពិសោធន៍របស់អ្នកគ្រប់គ្រង"),
    6: ("Results and Conclusion", "លទ្ធផល និងសេចក្ដីសន្និដ្ឋាន"),
}
