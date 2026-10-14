
from copy import deepcopy
from datetime import datetime, timezone

from campusflow_pro.sla.clock import utc_now
from campusflow_pro.sla.policy import calculate_due_at


def reopen_sla_cycle(
    ticket: dict,
    now: datetime | None = None,
) -> dict:
    """
    Prepare a new SLA cycle for a resolved ticket.

    Rules:
    - Only resolved tickets can be reopened.
    - Preserve the original created_at.
    - Change status to open.
    - Increment escalation_cycle.
    - Reset escalated_cycle to None.
    - Recalculate due_at using the ticket priority.
    - Update updated_at.
    - Clear resolved_at and started_at.
    - Never mutate the original ticket.

    The returned ticket must be committed together with
    a REOPEN audit event by the application layer.
    """

    if not isinstance(ticket, dict):
        raise TypeError("ticket must be a dictionary")

    if ticket.get("status") != "resolved":
        raise ValueError("Only resolved tickets can be reopened")

    cycle = ticket.get("escalation_cycle")

    if type(cycle) is not int or cycle < 0:
        raise ValueError("Invalid escalation_cycle")

    marker = ticket.get("escalated_cycle")

    if marker is not None:
        if (
            type(marker) is not int
            or marker < 0
            or marker > cycle
        ):
            raise ValueError("Invalid escalated_cycle")

    if now is None:
        now = utc_now()

    if not isinstance(now, datetime):
        raise TypeError("now must be a datetime object")

    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")

    now = now.astimezone(timezone.utc)

    priority = ticket.get("priority")

    # calculate_due_at validates the priority.
    due_at = calculate_due_at(priority, now)

    updated_ticket = deepcopy(ticket)

    updated_ticket["status"] = "open"
    updated_ticket["escalation_cycle"] = cycle + 1
    updated_ticket["escalated_cycle"] = None
    updated_ticket["due_at"] = due_at.isoformat()
    updated_ticket["updated_at"] = now.isoformat()

    updated_ticket["started_at"] = None
    updated_ticket["resolved_at"] = None

    return updated_ticket
