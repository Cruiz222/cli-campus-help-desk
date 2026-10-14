from datetime import datetime, timedelta, timezone

SLA_DURATIONS = {
    "critical": 60,
    "high": 240,
    "medium": 1440,
    "low": 2880,
}


def calculate_due_at(priority: str, cycle_start: datetime) -> datetime:
    if priority not in SLA_DURATIONS:
        raise ValueError("Unsupported priority type")

    if not isinstance(cycle_start, datetime):
        raise TypeError("cycle_start must be a datetime object")

    if cycle_start.tzinfo is None or cycle_start.utcoffset() is None:
        raise ValueError("cycle_start must be timezone-aware")

    cycle_start = cycle_start.astimezone(timezone.utc)

    duration = SLA_DURATIONS[priority]

    return cycle_start + timedelta(minutes=duration)