
"""SLA attention queue for CampusFlow Pro.

Schema-v2 tickets use their authoritative due_at deadline.
Legacy tickets without due_at retain the original SLA behavior.
"""

from datetime import datetime, timedelta, timezone

from campusflow_pro.ticket_fields import get_field
from campusflow_pro.sla.policy import calculate_due_at


LEGACY_SLA_HOURS = {
    "critical": 4,
    "high": 8,
    "medium": 24,
    "low": 72,
}

PRIORITY_RANK = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}

AT_RISK_FRACTION = 0.25

UNRESOLVED = {"open", "in_progress"}


def _to_utc(value, assume_local=False):
    """Convert a datetime or ISO timestamp to UTC."""

    if isinstance(value, str):
        value = datetime.fromisoformat(value)

    if not isinstance(value, datetime):
        raise TypeError("Expected a datetime or ISO timestamp.")

    if value.tzinfo is None or value.utcoffset() is None:
        if not assume_local:
            raise ValueError(
                "Timestamps must be timezone-aware."
            )

        value = value.astimezone()

    return value.astimezone(timezone.utc)


def _canonical_duration(priority):
    """Get the canonical SLA duration from the policy."""

    reference = datetime(
        2026, 1, 1, tzinfo=timezone.utc
    )

    return calculate_due_at(priority, reference) - reference


def sla_status(ticket, now):
    """Calculate the SLA status of a ticket."""

    priority = str(
        get_field(ticket, "priority")
    ).lower()

    if priority not in PRIORITY_RANK:
        raise ValueError(
            f"Unknown priority: {priority}"
        )

    current_time = _to_utc(now)

    due_at = (
        ticket.get("due_at")
        if isinstance(ticket, dict)
        else getattr(ticket, "due_at", None)
    )

    if due_at is not None:
        # Schema-v2 tickets have an authoritative deadline.
        deadline = _to_utc(due_at)
        limit = _canonical_duration(priority)

    else:
        # Compatibility with Engineer B's legacy tickets.
        limit = timedelta(
            hours=LEGACY_SLA_HOURS[priority]
        )

        created = _to_utc(
            get_field(ticket, "created_at"),
            assume_local=True,
        )

        deadline = created + limit

    remaining = deadline - current_time

    # The SLA engine considers a ticket overdue only
    # when current_time is strictly later than due_at.
    if remaining < timedelta(0):
        state = "breached"

    elif remaining <= limit * AT_RISK_FRACTION:
        state = "at_risk"

    else:
        state = "ok"

    return {
        "state": state,
        "priority": priority,
        "deadline": deadline,
        "remaining": remaining,
    }


def attention_queue(tickets, now=None):
    """Return unresolved tickets requiring SLA attention."""

    if now is None:
        now = datetime.now(timezone.utc)

    current_time = _to_utc(now)
    items = []

    for ticket in tickets:
        status = str(
            get_field(ticket, "status")
        ).lower()

        if status not in UNRESOLVED:
            continue

        info = sla_status(ticket, current_time)

        if info["state"] == "ok":
            continue

        items.append({
            "ticket": ticket,
            **info,
        })

    items.sort(
        key=lambda item: (
            0 if item["state"] == "breached" else 1,
            PRIORITY_RANK[item["priority"]],
            item["deadline"],
        )
    )

    return items
