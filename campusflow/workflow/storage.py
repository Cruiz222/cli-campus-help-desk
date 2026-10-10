import json


def save_tickets(tickets, filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(tickets, file, indent=4)


def load_tickets(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            tickets = json.load(file)

    except FileNotFoundError:
        return []

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in {filename}: {error}"
        ) from error

    if not isinstance(tickets, list):
        raise ValueError(
            "Ticket storage must contain a list."
        )

    seen_ids = set()

    for index, ticket in enumerate(tickets, start=1):
        if not isinstance(ticket, dict):
            raise ValueError(
                f"Ticket at position {index} must be a dictionary."
            )

        ticket_id = ticket.get("id")

        if not isinstance(ticket_id, str) or not ticket_id.strip():
            raise ValueError(
                f"Ticket at position {index} has an invalid ID."
            )

        if ticket_id in seen_ids:
            raise ValueError(
                f"Duplicate ticket ID detected: {ticket_id}"
            )

        seen_ids.add(ticket_id)

    return tickets