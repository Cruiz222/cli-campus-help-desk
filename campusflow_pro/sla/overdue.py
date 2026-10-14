
from datetime import datetime, timezone

from campusflow_pro.sla.clock import utc_now


def is_overdue(ticket: dict, now: datetime | None = None) -> bool:
    if not isinstance(ticket, dict):
        raise TypeError("ticket must be a dictionary")

    if ticket.get("status") not in (
        "open",
        "in_progress",
        "resolved",
    ):
        raise ValueError("Invalid ticket status")

    due_at = ticket.get("due_at")

    if not isinstance(due_at, str):
        raise ValueError("Ticket must have a valid due_at timestamp")

    try:
        deadline = datetime.fromisoformat(due_at)
    except ValueError as error:
        raise ValueError("Invalid due_at timestamp") from error

    if deadline.tzinfo is None or deadline.utcoffset() is None:
        raise ValueError("due_at must be timezone-aware")

    if now is None:
        now = utc_now()

    if not isinstance(now, datetime):
        raise TypeError("now must be a datetime object")

    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")

    if ticket["status"] == "resolved":
        return False

    deadline = deadline.astimezone(timezone.utc)
    now = now.astimezone(timezone.utc)

    return now > deadline
