"""SLA attention queue: unresolved tickets that are breached or at risk."""

from datetime import datetime, timedelta, timezone

from campusflow_pro.ticket_fields import get_field

SLA_HOURS = {"critical": 4, "high": 8, "medium": 24, "low": 72}
PRIORITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}
AT_RISK_FRACTION = 0.25
UNRESOLVED = {"open", "in_progress"}


def _to_utc(value):
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Timestamps must be timezone-aware.")
    return value.astimezone(timezone.utc)


def sla_status(ticket, now):
    priority = str(get_field(ticket, "priority")).lower()
    if priority not in SLA_HOURS:
        raise ValueError(f"Unknown priority: {priority}")

    limit = timedelta(hours=SLA_HOURS[priority])
    deadline = _to_utc(get_field(ticket, "created_at")) + limit
    remaining = deadline - _to_utc(now)

    if remaining <= timedelta(0):
        state = "breached"
    elif remaining <= limit * AT_RISK_FRACTION:
        state = "at_risk"
    else:
        state = "ok"

    return {"state": state, "priority": priority,
            "deadline": deadline, "remaining": remaining}


def attention_queue(tickets, now=None):
    """Breached first, then at-risk; ties by priority, then earliest deadline."""
    now = now or datetime.now(timezone.utc)
    items = []
    for ticket in tickets:
        if str(get_field(ticket, "status")).lower() not in UNRESOLVED:
            continue
        info = sla_status(ticket, now)
        if info["state"] == "ok":
            continue
        items.append({"ticket": ticket, **info})

    items.sort(key=lambda i: (
        0 if i["state"] == "breached" else 1,
        PRIORITY_RANK[i["priority"]],
        i["deadline"],
    ))
    return items