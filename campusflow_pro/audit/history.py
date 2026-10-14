"""Append-only audit history for CampusFlow Pro."""

from copy import deepcopy
from datetime import datetime, timezone


ALLOWED_EVENTS = {
    "CREATE",
    "ASSIGN",
    "START",
    "RESOLVE",
    "REOPEN",
    "ESCALATE",
}


class AuditHistory:
    """Record successful ticket operations without editing old events."""

    def __init__(self, clock=None):
        self._events = []
        self._next_id = 1
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def record(
        self,
        ticket_id,
        event_type,
        actor,
        before_status=None,
        after_status=None,
        details=None,
    ):
        """Append an event and return a copy of the recorded event."""

        event_type = event_type.upper()

        if event_type not in ALLOWED_EVENTS:
            raise ValueError(f"Unsupported event type: {event_type}")

        if not actor or not actor.strip():
            raise ValueError("Actor must not be empty.")

        if ticket_id is None:
            raise ValueError("Ticket ID must not be empty.")

        timestamp = self._clock()

        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("Timestamp must be timezone-aware.")

        event = {
            "event_id": self._next_id,
            "ticket_id": ticket_id,
            "event_type": event_type,
            "actor": actor.strip(),
            "timestamp": timestamp.astimezone(timezone.utc).isoformat(),
            "before_status": before_status,
            "after_status": after_status,
            "details": deepcopy(details) if details is not None else {},
        }

        self._events.append(event)
        self._next_id += 1

        return deepcopy(event)

    def all_events(self):
        """Return every event in chronological order."""

        events = sorted(
            self._events,
            key=lambda event: (event["timestamp"], event["event_id"]),
        )
        return deepcopy(events)

    def for_ticket(self, ticket_id):
        """Return chronological history for one ticket."""

        events = [
            event
            for event in self._events
            if event["ticket_id"] == ticket_id
        ]

        events.sort(
            key=lambda event: (event["timestamp"], event["event_id"])
        )

        return deepcopy(events)

    def count(self):
        """Return the number of recorded events."""
        return len(self._events)