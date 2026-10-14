
import re


TICKET_ID_PATTERN = re.compile(r"^T([0-9]+)$")


def next_ticket_id(tickets: list[dict]) -> str:
    """
    Generate the next ticket ID from persisted tickets.

    Examples:
        [] -> T001
        [T001, T002] -> T003
        [T001, T009] -> T010

    IDs are never based on list length.
    """

    if not isinstance(tickets, list):
        raise TypeError("tickets must be a list")

    highest = 0
    seen = set()

    for ticket in tickets:
        if not isinstance(ticket, dict):
            raise TypeError("each ticket must be a dictionary")

        ticket_id = ticket.get("id")

        if not isinstance(ticket_id, str):
            raise ValueError("ticket ID must be a string")

        match = TICKET_ID_PATTERN.fullmatch(ticket_id)

        if match is None:
            raise ValueError(f"Invalid ticket ID: {ticket_id}")

        if ticket_id in seen:
            raise ValueError(f"Duplicate ticket ID: {ticket_id}")

        seen.add(ticket_id)
        highest = max(highest, int(match.group(1)))

    return f"T{highest + 1:03d}"
