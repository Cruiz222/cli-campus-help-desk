
import re
from datetime import datetime, timezone

from campusflow.tickets import calculate_priority


SCHEMA_VERSION = 2

TICKET_ID_PATTERN = re.compile(r"^T[0-9]+$")

VALID_CATEGORIES = {"Network", "Hardware", "Software", "Other"}
VALID_URGENCIES = {"low", "medium", "high"}
VALID_PRIORITIES = {"low", "medium", "high", "critical"}
VALID_STATUSES = {"open", "in_progress", "resolved"}

VALID_EVENT_TYPES = {
    "CREATE",
    "ASSIGN",
    "START",
    "RESOLVE",
    "REOPEN",
    "ESCALATE",
}

REQUIRED_TICKET_FIELDS = {
    "id",
    "title",
    "category",
    "urgency",
    "affected_users",
    "priority",
    "status",
    "assigned_to",
    "created_at",
    "updated_at",
    "started_at",
    "resolved_at",
    "due_at",
    "escalation_cycle",
    "escalated_cycle",
}

REQUIRED_EVENT_FIELDS = {
    "event_id",
    "ticket_id",
    "event_type",
    "actor",
    "timestamp",
    "before_status",
    "after_status",
    "details",
}


def _timestamp(value, field_name):
    """Parse and normalize a timezone-aware ISO timestamp."""
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be an ISO timestamp")

    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError(
            f"{field_name} must be a valid ISO timestamp"
        ) from error

    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")

    return parsed.astimezone(timezone.utc)


def _optional_timestamp(value, field_name):
    if value is None:
        return None

    return _timestamp(value, field_name)


def _nonempty_string(value, field_name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _status_or_none(value, field_name):
    if value is not None and value not in VALID_STATUSES:
        raise ValueError(f"Invalid {field_name}")


def validate_ticket(ticket):
    """Validate one schema-v2 ticket."""
    if not isinstance(ticket, dict):
        raise ValueError("Each ticket must be a dictionary")

    missing = REQUIRED_TICKET_FIELDS - ticket.keys()

    if missing:
        raise ValueError(
            f"Missing ticket fields: {sorted(missing)}"
        )

    ticket_id = ticket["id"]

    if (
        not isinstance(ticket_id, str)
        or not TICKET_ID_PATTERN.fullmatch(ticket_id)
    ):
        raise ValueError("Invalid ticket ID")

    _nonempty_string(ticket["title"], "title")

    if ticket["category"] not in VALID_CATEGORIES:
        raise ValueError("Invalid ticket category")

    if ticket["urgency"] not in VALID_URGENCIES:
        raise ValueError("Invalid ticket urgency")

    affected = ticket["affected_users"]

    if type(affected) is not int or affected < 1:
        raise ValueError(
            "affected_users must be a positive integer"
        )

    if ticket["priority"] not in VALID_PRIORITIES:
        raise ValueError("Invalid ticket priority")

    expected_priority = calculate_priority(
        ticket["urgency"],
        affected,
    )

    if ticket["priority"] != expected_priority:
        raise ValueError(
            "Ticket priority does not match "
            "urgency and affected_users"
        )

    if ticket["status"] not in VALID_STATUSES:
        raise ValueError("Invalid ticket status")

    assigned = ticket["assigned_to"]

    if assigned is not None:
        _nonempty_string(assigned, "assigned_to")

    created = _timestamp(ticket["created_at"], "created_at")
    updated = _timestamp(ticket["updated_at"], "updated_at")
    due = _timestamp(ticket["due_at"], "due_at")

    started = _optional_timestamp(
        ticket["started_at"], "started_at"
    )

    resolved = _optional_timestamp(
        ticket["resolved_at"], "resolved_at"
    )

    if updated < created:
        raise ValueError(
            "updated_at cannot precede created_at"
        )

    if due <= created:
        raise ValueError(
            "due_at must follow created_at"
        )

    if started is not None and started < created:
        raise ValueError(
            "started_at cannot precede created_at"
        )

    if resolved is not None and resolved < created:
        raise ValueError(
            "resolved_at cannot precede created_at"
        )

    if ticket["status"] == "resolved" and resolved is None:
        raise ValueError(
            "Resolved ticket requires resolved_at"
        )

    if ticket["status"] != "resolved" and resolved is not None:
        raise ValueError(
            "Unresolved ticket cannot have resolved_at"
        )

    cycle = ticket["escalation_cycle"]
    marker = ticket["escalated_cycle"]

    if type(cycle) is not int or cycle < 0:
        raise ValueError("Invalid escalation_cycle")

    # The marker must be None or the current cycle.
    if marker is not None:
        if type(marker) is not int or marker != cycle:
            raise ValueError("Invalid escalated_cycle")


def validate_event(event, ticket_ids):
    """Validate one audit event."""
    if not isinstance(event, dict):
        raise ValueError("Each event must be a dictionary")

    missing = REQUIRED_EVENT_FIELDS - event.keys()

    if missing:
        raise ValueError(
            f"Missing event fields: {sorted(missing)}"
        )

    _nonempty_string(event["event_id"], "event_id")
    _nonempty_string(event["ticket_id"], "ticket_id")

    if event["ticket_id"] not in ticket_ids:
        raise ValueError(
            "Audit event references an unknown ticket"
        )

    if event["event_type"] not in VALID_EVENT_TYPES:
        raise ValueError("Invalid audit event type")

    _nonempty_string(event["actor"], "actor")
    _timestamp(event["timestamp"], "event timestamp")

    _status_or_none(
        event["before_status"], "before_status"
    )

    _status_or_none(
        event["after_status"], "after_status"
    )

    if not isinstance(event["details"], dict):
        raise ValueError(
            "Event details must be a dictionary"
        )

    if event["event_type"] == "ESCALATE":
        cycle = event["details"].get(
            "escalation_cycle"
        )

        if type(cycle) is not int or cycle < 0:
            raise ValueError(
                "ESCALATE event requires a valid "
                "escalation_cycle"
            )

        if event["before_status"] != event["after_status"]:
            raise ValueError(
                "ESCALATE must not change ticket status"
            )

        if event["before_status"] not in {
            "open",
            "in_progress",
        }:
            raise ValueError(
                "ESCALATE requires an unresolved status"
            )


def validate_document(document):
    """
    Validate a complete schema-v2 document.

    Checks:
    - Schema version
    - Ticket and event structures
    - Unique ticket and event IDs
    - Priority consistency
    - SLA metadata
    - One escalation event per ticket per cycle
    - Escalation marker/event consistency
    - Historical escalation cycles

    Returns the original document if valid.
    Does not mutate the document.
    """

    if not isinstance(document, dict):
        raise ValueError(
            "Document must be a dictionary"
        )

    if type(document.get("schema_version")) is not int:
        raise ValueError(
            "schema_version must be an integer"
        )

    if document["schema_version"] != SCHEMA_VERSION:
        raise ValueError(
            "Unsupported schema version"
        )

    tickets = document.get("tickets")
    events = document.get("events")

    if not isinstance(tickets, list):
        raise ValueError(
            "tickets must be a list"
        )

    if not isinstance(events, list):
        raise ValueError(
            "events must be a list"
        )

    # Validate all tickets and their IDs.
    ticket_ids = set()

    for ticket in tickets:
        validate_ticket(ticket)

        ticket_id = ticket["id"]

        if ticket_id in ticket_ids:
            raise ValueError(
                f"Duplicate ticket ID: {ticket_id}"
            )

        ticket_ids.add(ticket_id)

    # Validate all events and escalation history.
    event_ids = set()
    escalations = set()

    for event in events:
        validate_event(event, ticket_ids)

        event_id = event["event_id"]

        if event_id in event_ids:
            raise ValueError(
                f"Duplicate event ID: {event_id}"
            )

        event_ids.add(event_id)

        if event["event_type"] == "ESCALATE":
            key = (
                event["ticket_id"],
                event["details"]["escalation_cycle"],
            )

            if key in escalations:
                raise ValueError(
                    "Multiple ESCALATE events "
                    "for the same ticket and cycle"
                )

            escalations.add(key)

    # Validate escalation markers against audit events.
    for ticket in tickets:
        ticket_id = ticket["id"]
        current_cycle = ticket["escalation_cycle"]
        marker = ticket["escalated_cycle"]

        ticket_escalations = {
            cycle
            for event_ticket_id, cycle in escalations
            if event_ticket_id == ticket_id
        }

        # No event may refer to a future cycle.
        if any(
            cycle > current_cycle
            for cycle in ticket_escalations
        ):
            raise ValueError(
                f"Ticket {ticket_id} has an escalation "
                "event from a future cycle"
            )

        # A current-cycle marker requires an event.
        if (
            marker == current_cycle
            and current_cycle not in ticket_escalations
        ):
            raise ValueError(
                f"Ticket {ticket_id} is marked escalated "
                "without a matching audit event"
            )

        # A current-cycle event requires a marker.
        if (
            current_cycle in ticket_escalations
            and marker != current_cycle
        ):
            raise ValueError(
                f"Ticket {ticket_id} has an escalation "
                "event but an inconsistent marker"
            )

    return document
