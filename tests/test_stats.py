"""KPI definitions: the Resolution Rate ("Resolved") and chart data."""
import asyncio

from app.db import SessionLocal, init_db
from app.models import Conversation, Message, Source
from app.services.stats import chart_data, is_resolved


def _msg(i: int, direction: str, source: str | None = None, kind: str = "text") -> Message:
    return Message(id=i, conversation_id=1, user_id=1, direction=direction, message_type=kind,
                   content="x", response_source=source)


def _conv(support_status=None, resolution_status="unresolved") -> Conversation:
    return Conversation(id=1, user_id=1, support_status=support_status, resolution_status=resolution_status)


def test_answered_by_bot_is_resolved():
    messages = [_msg(1, "incoming"), _msg(2, "outgoing", Source.FAQ)]
    assert is_resolved(_conv(), messages, bad_feedback=False) is True


def test_last_answer_fallback_is_unresolved():
    messages = [_msg(1, "incoming"), _msg(2, "outgoing", Source.FAQ),
                _msg(3, "incoming"), _msg(4, "outgoing", Source.FALLBACK)]
    assert is_resolved(_conv(), messages, bad_feedback=False) is False


def test_fallback_then_rephrased_and_answered_is_resolved():
    messages = [_msg(1, "incoming"), _msg(2, "outgoing", Source.FALLBACK),
                _msg(3, "incoming"), _msg(4, "outgoing", Source.KNOWLEDGE)]
    assert is_resolved(_conv(), messages, bad_feedback=False) is True


def test_negative_feedback_is_unresolved():
    messages = [_msg(1, "incoming"), _msg(2, "outgoing", Source.AI)]
    assert is_resolved(_conv(), messages, bad_feedback=True) is False


def test_open_handoff_is_unresolved_until_agent_resolves():
    messages = [_msg(1, "incoming"), _msg(2, "outgoing", Source.COMMAND)]
    assert is_resolved(_conv("In Progress"), messages, bad_feedback=False) is False
    assert is_resolved(_conv("Closed"), messages, bad_feedback=False) is False  # closed, not solved
    assert is_resolved(_conv("Resolved", "resolved"), messages, bad_feedback=True) is True


def test_conversation_without_text_is_not_counted():
    assert is_resolved(_conv(), [_msg(1, "incoming", kind="image")], bad_feedback=False) is None


def test_chart_data_shape():
    async def run():
        await init_db()
        async with SessionLocal() as session:
            return await chart_data(session, days=7)
    data = asyncio.run(run())
    assert len(data["labels"]) == len(data["incoming"]) == len(data["total_users"]) == 7
    assert isinstance(data["sources"], dict) and isinstance(data["popular_questions"], list)
