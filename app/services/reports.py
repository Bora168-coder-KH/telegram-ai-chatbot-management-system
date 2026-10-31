"""Reports for a date range, and export to Excel (openpyxl) and PDF (fpdf2).

The PDF embeds Noto Sans with Noto Sans Khmer as a fallback and uses text
shaping (uharfbuzz), so Khmer questions and answers print correctly.
"""
import io
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.i18n import button_key
from app.models import Conversation, Feedback, Message, TelegramUser, UnknownQuestion
from app.services.stats import resolution
from app.services.text import normalize
from app.services.validators import scrub_contacts

FONTS = Path(__file__).resolve().parent.parent / "web" / "static" / "fonts"


def date_range(start: str | None, end: str | None, default_days: int = 30) -> tuple[date, date]:
    """Parse ?start=YYYY-MM-DD&end=YYYY-MM-DD; default: the last 30 days. `end` is included."""
    today = datetime.now().date()

    def parse(value: str | None, fallback: date) -> date:
        try:
            return date.fromisoformat(value) if value else fallback
        except ValueError:
            return fallback
    end_day = parse(end, today)
    start_day = parse(start, end_day - timedelta(days=default_days - 1))
    if start_day > end_day:
        start_day, end_day = end_day, start_day
    return start_day, end_day


async def build_report(session: AsyncSession, start: date, end: date) -> dict:
    since = datetime.combine(start, datetime.min.time())
    until = datetime.combine(end + timedelta(days=1), datetime.min.time())

    messages = (await session.execute(
        select(Message.created_at, Message.direction, Message.response_source, Message.message_type, Message.content)
        .where(Message.created_at >= since, Message.created_at < until)
    )).all()
    daily: dict[date, Counter] = {start + timedelta(days=i): Counter() for i in range((end - start).days + 1)}
    sources: Counter = Counter()
    questions: Counter = Counter()
    for created, direction, source, kind, content in messages:
        daily[created.date()][direction] += 1
        if direction == "outgoing" and source:
            sources[source] += 1
        if direction == "incoming" and kind == "text" and content and not content.startswith("/") \
                and button_key(content) is None:
            questions[normalize(scrub_contacts(content))] += 1

    new_users = (await session.execute(select(TelegramUser.first_interaction_at).where(
        TelegramUser.first_interaction_at >= since, TelegramUser.first_interaction_at < until))).scalars().all()
    for joined in new_users:
        daily[joined.date()]["new_users"] += 1

    conversations = (await session.execute(select(func.count(Conversation.id)).where(
        Conversation.started_at >= since, Conversation.started_at < until))).scalar_one()
    handoffs = (await session.execute(select(func.count(Conversation.id)).where(
        Conversation.handoff_requested_at >= since, Conversation.handoff_requested_at < until))).scalar_one()
    ratings = (await session.execute(select(Feedback.rating).where(
        Feedback.created_at >= since, Feedback.created_at < until))).scalars().all()
    unanswered = (await session.execute(
        select(UnknownQuestion).where(UnknownQuestion.status == "open", UnknownQuestion.last_asked_at >= since)
        .order_by(UnknownQuestion.frequency.desc()).limit(20)
    )).scalars().all()
    resolved = await resolution(session, since, until)

    incoming = sum(day["incoming"] for day in daily.values())
    outgoing = sum(day["outgoing"] for day in daily.values())
    fallback = sources.get("Fallback", 0)
    return {
        "start": start, "end": end,
        "summary": [
            ("New users", len(new_users)),
            ("Conversations", conversations),
            ("Incoming messages", incoming),
            ("Outgoing messages", outgoing),
            ("Resolution rate", f"{resolved['rate']}% ({resolved['resolved']} of {resolved['counted']})"),
            ("Fallback answers", fallback),
            ("AI answers", sources.get("AI", 0)),
            ("Human handoffs", handoffs),
            ("Feedback count", len(ratings)),
            ("Average rating (1-5)", round(sum(ratings) / len(ratings), 2) if ratings else "-"),
        ],
        "daily": [(day, c["new_users"], c["incoming"], c["outgoing"]) for day, c in daily.items()],
        "sources": sources.most_common(),
        "top_questions": [(q, n) for q, n in questions.most_common(15) if q],
        "unanswered": [(u.question, u.frequency) for u in unanswered],
    }


def to_excel(report: dict) -> bytes:
    from openpyxl import Workbook
    from openpyxl.styles import Font

    book = Workbook()
    bold = Font(bold=True)

    def sheet(title: str, header: list[str], rows, first: bool = False):
        ws = book.active if first else book.create_sheet()
        ws.title = title
        ws.append(header)
        for cell in ws[1]:
            cell.font = bold
        for row in rows:
            ws.append(list(row))
        for column in ws.columns:
            width = max(len(str(c.value or "")) for c in column)
            ws.column_dimensions[column[0].column_letter].width = min(max(width + 2, 10), 70)

    period = f"{report['start']} to {report['end']}"
    sheet("Summary", ["Metric", period], report["summary"], first=True)
    sheet("Daily", ["Date", "New users", "Incoming", "Outgoing"], report["daily"])
    sheet("Response sources", ["Source", "Answers"], report["sources"])
    sheet("Top questions", ["Question", "Times asked"], report["top_questions"])
    sheet("Unanswered", ["Question", "Times asked"], report["unanswered"])
    buffer = io.BytesIO()
    book.save(buffer)
    return buffer.getvalue()


def to_pdf(report: dict) -> bytes:
    from fpdf import FPDF
    from fpdf.fonts import FontFace

    pdf = FPDF()
    pdf.add_font("Noto", "", str(FONTS / "NotoSans-Regular.ttf"))
    pdf.add_font("Noto", "B", str(FONTS / "NotoSans-Bold.ttf"))
    pdf.add_font("NotoKhmer", "", str(FONTS / "NotoSansKhmer-Regular.ttf"))
    pdf.add_font("NotoKhmer", "B", str(FONTS / "NotoSansKhmer-Bold.ttf"))
    pdf.set_fallback_fonts(["NotoKhmer"])
    pdf.set_text_shaping(True)
    pdf.set_auto_page_break(True, margin=15)
    pdf.add_page()
    pdf.set_font("Noto", "B", 16)
    pdf.cell(0, 10, "AI Chatbot Report", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Noto", "", 10)
    pdf.cell(0, 6, f"Period: {report['start']} to {report['end']}", new_x="LMARGIN", new_y="NEXT")
    heading = FontFace(emphasis="BOLD", fill_color=(230, 238, 244))

    def table(title: str, header: tuple, rows, widths: tuple):
        pdf.ln(4)
        pdf.set_font("Noto", "B", 12)
        pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Noto", "", 9)
        if not rows:
            pdf.cell(0, 6, "No data for this period.", new_x="LMARGIN", new_y="NEXT")
            return
        with pdf.table(col_widths=widths, headings_style=heading, line_height=6) as t:
            t.row([str(h) for h in header])
            for row in rows:
                t.row([str(v) for v in row])

    table("Summary", ("Metric", "Value"), report["summary"], (60, 40))
    table("Response sources", ("Source", "Answers"), report["sources"], (60, 40))
    table("Top questions", ("Question", "Times asked"), report["top_questions"], (80, 20))
    table("Unanswered questions", ("Question", "Times asked"), report["unanswered"], (80, 20))
    table("Daily activity", ("Date", "New users", "Incoming", "Outgoing"), report["daily"], (40, 20, 20, 20))
    return bytes(pdf.output())
