
from copy import deepcopy
from datetime import datetime, timezone
from typing import Callable

from campusflow_pro.sla.clock import utc_now
from campusflow_pro.sla.overdue import is_overdue


def escalate_overdue(
    tickets: list,
    events: list,
    now: datetime | None = None,
    actor: str = "system",
    event_factory: Callable | None = None,
) -> dict:
    """
    Prepare escalations for overdue tickets.

    Rules:
    - Only unresolved, overdue tickets can be escalated.
    - Each ticket can be escalated once per SLA cycle.
    - Repeated checks do not create duplicate events.
    - Escalation does not change ticket status, priority,
      or assignment.
    - Every new escalation produces one ESCALATE event.
    - Original tickets and events are never mutated.

    Returns updated copies for the application layer
    to persist atomically.
    """

    # Validate collections.
    if not isinstance(tickets, list):
        raise TypeError("tickets must be a list")

    if not isinstance(events, list):
        raise TypeError("events must be a list")

    # Validate event factory.
    if not callable(event_factory):
        raise TypeError("event_factory must be callable")

    # Resolve current time.
    if now is None:
        now = utc_now()

    if not isinstance(now, datetime):
        raise TypeError("now must be a datetime object")

    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")

    now = now.astimezone(timezone.utc)
    timestamp = now.isoformat()

    # Validate actor.
    if not isinstance(actor, str) or not actor.strip():
        raise ValueError("actor must be a non-empty string")

    actor = actor.strip()

    # Work on copies to avoid partial input mutation.
    updated_tickets = deepcopy(tickets)
    updated_events = deepcopy(events)

    newly_escalated = 0
    already_escalated = 0

    # Evaluate every ticket.
    for ticket in updated_tickets:

        # Validate ticket structure.
        if not isinstance(ticket, dict):
            raise TypeError("each ticket must be a dictionary")

        # Validate SLA metadata.
        cycle = ticket.get("escalation_cycle")

        if type(cycle) is not int or cycle < 0:
            raise ValueError(
                f"Invalid escalation_cycle for ticket "
                f"{ticket.get('id')}"
            )

        marker = ticket.get("escalated_cycle")

        if marker is not None:
            if (
                type(marker) is not int
                or marker < 0
                or marker > cycle
            ):
                raise ValueError(
                    f"Invalid escalated_cycle for ticket "
                    f"{ticket.get('id')}"
                )

        # Skip tickets that are not overdue.
        if not is_overdue(ticket, now):
            continue

        # Ticket was already escalated in this cycle.
        if marker == cycle:
            already_escalated += 1
            continue

        ticket_id = ticket.get("id")

        if not isinstance(ticket_id, str) or not ticket_id.strip():
            raise ValueError("Ticket must have a valid ID")

        status = ticket["status"]

        # Engineer B's event factory creates the event.
        event = event_factory(
            event_type="ESCALATE",
            ticket_id=ticket_id,
            actor=actor,
            timestamp=timestamp,
            before_status=status,
            after_status=status,
            details={
                "escalation_cycle": cycle,
            },
        )

        if not isinstance(event, dict):
            raise TypeError(
                "event_factory must return a dictionary"
            )

        # Validate the minimum event contract.
        required_fields = {
            "event_id",
            "event_type",
            "ticket_id",
            "actor",
            "timestamp",
            "before_status",
            "after_status",
            "details",
        }

        if not required_fields.issubset(event):
            raise ValueError(
                "event_factory returned an incomplete audit event"
            )

        if (
            event["event_type"] != "ESCALATE"
            or event["ticket_id"] != ticket_id
            or event["before_status"] != status
            or event["after_status"] != status
            or event["details"] != {"escalation_cycle": cycle}
            or event["actor"] != actor
            or event["timestamp"] != timestamp
        ):
            raise ValueError(
                "event_factory returned inconsistent escalation data"
            )

        if (
            not isinstance(event["event_id"], str)
            or not event["event_id"].strip()
        ):
            raise ValueError("Audit event must have a valid event_id")

        if any(
            existing.get("event_id") == event["event_id"]
            for existing in updated_events
        ):
            raise ValueError("Duplicate audit event ID")

        # Update the copied state only after event validation.
        updated_events.append(event)
        ticket["escalated_cycle"] = cycle
        ticket["updated_at"] = timestamp

        newly_escalated += 1

    return {
        "tickets": updated_tickets,
        "events": updated_events,
        "newly_escalated": newly_escalated,
        "already_escalated": already_escalated,
    }
