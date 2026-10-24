"""Run the labelled test questions through the Response Routing Logic and score the answers.

    python -m scripts.evaluate_questions [docs/evaluation/test_questions.csv]

It uses a fresh temporary database with the seed data and all mock FAQs, so the
real database is never touched. AI is switched off, so the result shows what the
rules, intents, FAQ and Knowledge Base can answer on their own.
A row passes when the source matches and (for FAQ / Intent / KnowledgeBase) the
matched item is the expected one.
"""
import asyncio
import csv
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path

DEFAULT_FILE = Path("docs/evaluation/test_questions.csv")


async def evaluate(rows: list[dict]) -> list[dict]:
    from sqlalchemy import select

    from app.db import SessionLocal, init_db
    from app.mock_data import seed_mock_faqs
    from app.models import FAQ, KnowledgeArticle, Source
    from app.seed import seed_defaults
    from app.services import router
    from app.services.users import get_or_create_user

    await init_db()
    results = []
    async with SessionLocal() as session:
        await seed_defaults(session)
        await seed_mock_faqs(session)
        user, _ = await get_or_create_user(session, 1, "eval", "Evaluation")
        for row in rows:
            user.language = row["lang"]
            reply = await router.route_message(session, user, row["question"])
            matched = "-"
            if reply.source == Source.FAQ:
                faq = (await session.execute(select(FAQ).where(FAQ.answer == reply.text))).scalars().first()
                matched = faq.question if faq else "?"
            elif reply.source == Source.INTENT:
                matched = reply.intent or "?"
            elif reply.source == Source.KNOWLEDGE:
                article = (await session.execute(
                    select(KnowledgeArticle).where(KnowledgeArticle.content == reply.text))).scalars().first()
                matched = article.title if article else "?"
            ok = reply.source == row["expected_source"] and (
                row["expected_target"] == "-" or matched == row["expected_target"])
            results.append({**row, "got_source": reply.source, "got_target": matched, "pass": ok})
    return results


def report(results: list[dict]) -> str:
    total = len(results)
    passed = sum(r["pass"] for r in results)
    lines = [f"Passed {passed} of {total} ({passed / total * 100:.0f}%)", ""]
    by_lang, by_kind = Counter(), Counter()
    for r in results:
        by_lang[(r["lang"], r["pass"])] += 1
        by_kind[(r["kind"].split(" (")[0], r["pass"])] += 1
    for lang in sorted({r["lang"] for r in results}):
        ok, all_ = by_lang[(lang, True)], by_lang[(lang, True)] + by_lang[(lang, False)]
        lines.append(f"  {lang}: {ok}/{all_}")
    lines.append("")
    lines.append("Failures:")
    for r in results:
        if not r["pass"]:
            lines.append(f"  #{r['id']} [{r['lang']}] {r['question']!r}: expected {r['expected_source']} "
                         f"{r['expected_target']!r}, got {r['got_source']} {r['got_target']!r}")
    return "\n".join(lines)


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_FILE
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(report(asyncio.run(evaluate(rows))))


if __name__ == "__main__":
    # a throwaway database, set before the app modules read the settings
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{tempfile.mkdtemp()}/evaluation.db"
    os.environ["AI_API_KEY"] = ""
    os.environ["ADMIN_PASSWORD"] = "evaluation-only"  # the seed needs one; this database is thrown away
    main()
