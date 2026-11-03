# AI Chatbot Video — Production Pack

Everything needed to make the project video in **Khmer (Version A)** and **English (Version B)**.

- **Length:** about 6:46 · **Scenes:** 49 (SC-001 to SC-049) · **Chapters:** 6
- Every file uses the same scene IDs, so you can replace one scene without touching the rest.

## Read in this order

| # | Part | File |
|---|---|---|
| 1–2 | Video concept, length and six-chapter structure | [01-Scripts/01-Video-Concept-and-Structure.md](01-Scripts/01-Video-Concept-and-Structure.md) |
| 3 | Character reference prompts (Sokha, Dara) | [02-Character-References/Character-Reference-Prompts.md](02-Character-References/Character-Reference-Prompts.md) |
| 4 | Full bilingual storyboard (all 49 scenes) | [01-Scripts/02-Bilingual-Storyboard.md](01-Scripts/02-Bilingual-Storyboard.md) |
| 5 | Full Khmer narration script | [01-Scripts/Khmer/Script-KH.md](01-Scripts/Khmer/Script-KH.md) |
| 6 | Full English narration script | [01-Scripts/English/Script-EN.md](01-Scripts/English/Script-EN.md) |
| 7 | AI video prompts (copy-paste list) | [03-AI-Generated-Scenes/AI-Video-Prompts.md](03-AI-Generated-Scenes/AI-Video-Prompts.md) |
| 8 | Editing timeline and production plan | [09-Editing-Project/Editing-Timeline.md](09-Editing-Project/Editing-Timeline.md) |
| 9 | Subtitles (estimated times) | [08-Subtitles/](08-Subtitles/) |
| 10 | Final checklist + changes to approve | [10-Final-Exports/Production-Checklist.md](10-Final-Exports/Production-Checklist.md) |

**Start with the checklist, section A.** It lists the few words I changed in the original script so the video matches the real software.

## Folder structure

```
AI-Chatbot-Video/
  01-Scripts/            concept, storyboard, Khmer/ and English/ scripts
  02-Character-References/
  03-AI-Generated-Scenes/   SC-0XX-AI.mp4
  04-Telegram-Recordings/   SC-0XX-TG.mp4
  05-Dashboard-Recordings/  SC-0XX-DB.mp4
  06-Voiceovers/Khmer/      SC-0XX-KH.wav
  06-Voiceovers/English/    SC-0XX-EN.wav
  07-Music-and-SFX/
  08-Subtitles/
  09-Editing-Project/
  10-Final-Exports/         scenes/SC-0XX-KH.mp4, SC-0XX-EN.mp4, full videos
```

The two draft videos are saved in `10-Final-Exports/` (`AI-Chatbot-Video-KH.mp4`, `AI-Chatbot-Video-EN.mp4`). Other video and audio files are not stored in Git (see `.gitignore`); keep them on a shared drive.

## Changing the text later

All scene text lives in one file: `01-Scripts/_generator/scenes.py`.
After you edit it, rebuild every document and both subtitle files with one command (run from this folder):

```bash
python3 01-Scripts/_generator/build.py .
```
