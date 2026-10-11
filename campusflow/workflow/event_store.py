import json
import os
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


EVENT_TYPES = {
    "ticket_created",
    "mentor_assigned",
    "ticket_started",
    "ticket_resolved",
    "ticket_reopened",
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def append_event(filename, event_type, ticket, actor):
    """
    Append one immutable historical event.

    Never rewrite previous events.
    """
    if event_type not in EVENT_TYPES:
        raise ValueError(f"Unsupported event: {event_type}")

    if not isinstance(ticket, dict):
        raise ValueError("Ticket must be a dictionary.")

    ticket_id = ticket.get("id")

    if not isinstance(ticket_id, str) or not ticket_id:
        raise ValueError("Ticket must have a valid ID.")

    if not isinstance(actor, str) or not actor.strip():
        raise ValueError("Actor is required.")

    event = {
        "event_id": str(uuid4()),
        "event_type": event_type,
        "ticket_id": ticket_id,
        "actor": actor.strip(),
        "occurred_at": utc_now(),
        "ticket_snapshot": deepcopy(ticket),
    }

    # Serialize before opening the file.
    # This prevents serialization errors from writing partial JSON.
    encoded = (
        json.dumps(event, ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    # O_APPEND makes each write append at the end of the file.
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_APPEND,
        0o600,
    )

    try:
        written = os.write(descriptor, encoded)

        if written != len(encoded):
            raise OSError("Incomplete event write.")

        os.fsync(descriptor)

    finally:
        os.close(descriptor)

    return deepcopy(event)


def load_events(filename):
    """
    Read the event history without modifying it.
    """
    path = Path(filename)

    if not path.exists():
        return []

    events = []
    seen_event_ids = set()

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                raise ValueError(
                    f"Empty event at line {line_number}."
                )

            try:
                event = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Corrupted event at line {line_number}."
                ) from error

            if not isinstance(event, dict):
                raise ValueError("Event must be a dictionary.")

            required = {
                "event_id",
                "event_type",
                "ticket_id",
                "actor",
                "occurred_at",
                "ticket_snapshot",
            }

            if not required.issubset(event):
                raise ValueError(
                    f"Incomplete event at line {line_number}."
                )

            if event["event_type"] not in EVENT_TYPES:
                raise ValueError(
                    f"Unknown event at line {line_number}."
                )

            event_id = event["event_id"]

            if not isinstance(event_id, str) or not event_id:
                raise ValueError("Invalid event ID.")

            if event_id in seen_event_ids:
                raise ValueError("Duplicate event ID.")

            seen_event_ids.add(event_id)

            ticket = event["ticket_snapshot"]

            if not isinstance(ticket, dict):
                raise ValueError("Invalid ticket snapshot.")

            if (
                not isinstance(event["ticket_id"], str)
                or ticket.get("id") != event["ticket_id"]
            ):
                raise ValueError("Event ticket ID mismatch.")

            if (
                not isinstance(event["actor"], str)
                or not event["actor"].strip()
            ):
                raise ValueError("Invalid event actor.")

            try:
                datetime.fromisoformat(event["occurred_at"])
            except (TypeError, ValueError) as error:
                raise ValueError(
                    "Invalid event timestamp."
                ) from error

            events.append(event)

    return events


def rebuild_tickets(filename):
    """
    Reconstruct the current ticket list from all events.
    """
    events = load_events(filename)

    tickets_by_id = {}

    expected_status = {
        "ticket_created": "open",
        "ticket_started": "in_progress",
        "ticket_resolved": "resolved",
        "ticket_reopened": "open",
    }

    for event in events:
        ticket_id = event["ticket_id"]
        event_type = event["event_type"]
        snapshot = deepcopy(event["ticket_snapshot"])

        previous = tickets_by_id.get(ticket_id)

        if event_type == "ticket_created":
            if previous is not None:
                raise ValueError(
                    f"Duplicate ticket creation: {ticket_id}"
                )

            if snapshot.get("status") != "open":
                raise ValueError("New ticket must be open.")

            tickets_by_id[ticket_id] = snapshot
            continue

        if previous is None:
            raise ValueError(
                f"Event references unknown ticket: {ticket_id}"
            )

        # Identity and creation information cannot change.
        immutable_fields = (
            "id",
            "title",
            "category",
            "urgency",
            "affected_users",
            "priority",
            "issuer",
            "created_at",
        )

        for field in immutable_fields:
            if snapshot.get(field) != previous.get(field):
                raise ValueError(
                    f"Immutable field changed: {field}"
                )

        if event_type == "mentor_assigned":
            if previous.get("status") != "open":
                raise ValueError(
                    "Only open tickets can be assigned."
                )

            if previous.get("assigned_to") is not None:
                raise ValueError(
                    "Ticket already has a mentor."
                )

            if not snapshot.get("assigned_to"):
                raise ValueError("Mentor is required.")

            if snapshot.get("status") != "open":
                raise ValueError("Assignment cannot change status.")

        elif event_type == "ticket_started":
            if previous.get("status") != "open":
                raise ValueError("Ticket must be open.")

            if not previous.get("assigned_to"):
                raise ValueError("Ticket must be assigned.")

        elif event_type == "ticket_resolved":
            if previous.get("status") != "in_progress":
                raise ValueError("Ticket must be in progress.")

        elif event_type == "ticket_reopened":
            if previous.get("status") != "resolved":
                raise ValueError("Ticket must be resolved.")

        if event_type in expected_status:
            if snapshot.get("status") != expected_status[event_type]:
                raise ValueError(
                    f"Invalid status for {event_type}"
                )

        if snapshot.get("assigned_to") != previous.get("assigned_to"):
            if event_type != "mentor_assigned":
                raise ValueError(
                    "Mentor changed outside assignment event."
                )

        tickets_by_id[ticket_id] = snapshot

    return list(tickets_by_id.values())


def get_ticket_history(filename, ticket_id):
    """
    Return all historical events for one ticket.
    """
    return [
        event
        for event in load_events(filename)
        if event["ticket_id"] == ticket_id
    ]