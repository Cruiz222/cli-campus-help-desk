MENTORS = (
    "Mr Godswill Sekav Apya",
    "Mr Kingsley Nnaemeka",
    "Mr Gabriel",
    "Mr Israel",
    "Mr Ayuba",
    "Mr Emmanuel",
)


def assign_mentor_automatically(tickets, ticket):
    if ticket["status"] != "open":
        raise ValueError("Only open tickets can be assigned.")

    if ticket.get("assigned_to") is not None:
        raise ValueError("Ticket is already assigned.")

    workload = {mentor: 0 for mentor in MENTORS}

    for existing in tickets:
        if existing["status"] in ("open", "in_progress"):
            mentor = existing.get("assigned_to")

            if mentor in workload:
                workload[mentor] += 1

    selected_mentor = min(
        MENTORS,
        key=lambda mentor: workload[mentor],
    )

    ticket["assigned_to"] = selected_mentor
    return selected_mentor


def get_mentor_tickets(tickets, mentor):
    if mentor not in MENTORS:
        raise ValueError("Unknown mentor.")

    return [
        ticket.copy()
        for ticket in tickets
        if ticket.get("assigned_to") == mentor
    ]


def get_mentor_queue(tickets, mentor):
    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    pending = [
        ticket
        for ticket in get_mentor_tickets(tickets, mentor)
        if ticket["status"] == "open"
    ]

    return sorted(
        pending,
        key=lambda ticket: (
            priority_order[ticket["priority"]],
            int(ticket["id"][1:]),
        ),
    )


def mentor_has_active_ticket(tickets, mentor):
    return any(
        ticket.get("assigned_to") == mentor
        and ticket["status"] == "in_progress"
        for ticket in tickets
    )


def start_mentor_ticket(tickets, ticket_id, mentor):
    if mentor not in MENTORS:
        raise ValueError("Unknown mentor.")

    ticket = next(
        (item for item in tickets if item["id"] == ticket_id),
        None,
    )

    if ticket is None:
        raise ValueError("Ticket not found.")

    if ticket.get("assigned_to") != mentor:
        raise ValueError("This ticket is not assigned to you.")

    if ticket["status"] != "open":
        raise ValueError("Only open tickets can be started.")

    if mentor_has_active_ticket(tickets, mentor):
        raise ValueError(
            "You already have an in-progress ticket. "
            "Complete it before starting another."
        )

    from campusflow.workflow.ticket_status import update_ticket_status

    return update_ticket_status(tickets, ticket_id, "in_progress")


def resolve_mentor_ticket(tickets, ticket_id, mentor):
    if mentor not in MENTORS:
        raise ValueError("Unknown mentor.")

    ticket = next(
        (item for item in tickets if item["id"] == ticket_id),
        None,
    )

    if ticket is None:
        raise ValueError("Ticket not found.")

    if ticket.get("assigned_to") != mentor:
        raise ValueError("This ticket is not assigned to you.")

    from campusflow.workflow.ticket_status import update_ticket_status

    return update_ticket_status(tickets, ticket_id, "resolved")