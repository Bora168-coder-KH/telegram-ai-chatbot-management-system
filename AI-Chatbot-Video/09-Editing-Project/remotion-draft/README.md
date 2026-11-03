# Draft video (Remotion)

This is the **draft animatic** of the project video: all 49 scenes, both languages, burned-in subtitles.
It follows `01-Scripts/02-Bilingual-Storyboard.md` scene by scene.

## What is real and what is a placeholder

| Part | In this draft |
|---|---|
| Dashboard screens | **Real screenshots** of the system (branch `feature/all-screens`), with demo data |
| Bot messages in the phone | **Real bot texts**, captured by playing the story through the project's own bot code |
| Sokha and Dara | Flat 2D drawings (replace with AI clips later if you want) |
| Presenter (SC-002, SC-048) and team photos (SC-003) | Placeholders — add the real video and photos |
| Voice-over and music | **None yet** — record the voice from `01-Scripts/Khmer` and `01-Scripts/English` |

## Preview and edit on your computer

```bash
npm install
```

```bash
npm run studio
```

Then open the link it prints. Pick **VideoKH** or **VideoEN**.

## Render

```bash
npm run render:kh
```

```bash
npm run render:en
```

## Where to change things

- Scene timing and subtitles come from `01-Scripts/_generator/scenes.py`. After you change the script, run `python3 01-Scripts/_generator/build.py .` (in `AI-Chatbot-Video/`) and then `python3 export.py` (in this folder).
- Each scene's drawing is in `src/scenes/Scenes.tsx` (search for `S020`, `S031`, …).
- Characters: `src/characters/People.tsx`. Rooms: `src/characters/Sets.tsx`.
- Screenshots: `public/shots/` (made with `../demo-capture/`).

Remotion is free for individuals and very small teams. Check https://www.remotion.dev/license for other uses.
