"""Times are stored in UTC; the dashboard shows and accepts local time (TIMEZONE in .env)."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.config import settings


def _zone() -> ZoneInfo:
    return ZoneInfo(settings.timezone)


def to_local(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.replace(tzinfo=timezone.utc).astimezone(_zone()).replace(tzinfo=None)


def local_to_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=_zone()).astimezone(timezone.utc).replace(tzinfo=None)


def localtime(value: datetime | None, fmt: str = "%Y-%m-%d %H:%M") -> str:
    """Jinja filter: {{ m.created_at | localtime }}"""
    local = to_local(value)
    return local.strftime(fmt) if local else "-"
