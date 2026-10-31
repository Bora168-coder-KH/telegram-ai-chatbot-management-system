"""Reports page with export to Excel and PDF."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Admin
from app.services import logs
from app.services.reports import build_report, date_range, to_excel, to_pdf
from app.web.deps import get_session, render, require

router = APIRouter()


@router.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request, start: str = "", end: str = "", admin: Admin = Depends(require("report")),
                       session: AsyncSession = Depends(get_session)):
    first, last = date_range(start, end)
    report = await build_report(session, first, last)
    return await render(request, "reports.html", admin, session, "Reports", report=report)


@router.get("/reports/export.{fmt}")
async def reports_export(fmt: str, start: str = "", end: str = "", admin: Admin = Depends(require("report")),
                         session: AsyncSession = Depends(get_session)):
    first, last = date_range(start, end)
    report = await build_report(session, first, last)
    name = f"chatbot-report-{first}-to-{last}.{fmt}"
    if fmt == "xlsx":
        body, media = to_excel(report), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif fmt == "pdf":
        body, media = to_pdf(report), "application/pdf"
    else:
        return Response("Unknown format", status_code=404)
    await logs.audit(session, admin.email, f"Exported report ({fmt})", details=f"{first} to {last}")
    return Response(body, media_type=media, headers={"Content-Disposition": f'attachment; filename="{name}"'})
