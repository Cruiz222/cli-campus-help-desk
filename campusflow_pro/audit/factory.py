
from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from campusflow_pro.audit.history import ALLOWED_EVENTS


def make_event(
    *,
    event_type,
    ticket_id,
    actor,
    timestamp,
    before_status=None,
    after_status=None,
    details=None,
):
    """Create a schema-v2-compatible audit event."""

    if not isinstance(event_type, str):
        raise ValueError("event_type must be a string")

    event_type = event_type.upper()

    if event_type not in ALLOWED_EVENTS:
        raise ValueError("Unsupported audit event type")

    if not isinstance(ticket_id, str) or not ticket_id.strip():
        raise ValueError("Invalid ticket ID")

    if not isinstance(actor, str) or not actor.strip():
        raise ValueError("Invalid actor")

    if isinstance(timestamp, datetime):
        parsed = timestamp
    elif isinstance(timestamp, str):
        try:
            parsed = datetime.fromisoformat(timestamp)
        except ValueError as error:
            raise ValueError("Invalid event timestamp") from error
    else:
        raise ValueError("Invalid event timestamp")

    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Event timestamp must be timezone-aware")

    return {
        "event_id": str(uuid4()),
        "ticket_id": ticket_id.strip().upper(),
        "event_type": event_type,
        "actor": actor.strip(),
        "timestamp": parsed.astimezone(timezone.utc).isoformat(),
        "before_status": before_status,
        "after_status": after_status,
        "details": deepcopy(details) if details is not None else {},
    }