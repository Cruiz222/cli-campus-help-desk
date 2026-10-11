from copy import deepcopy

from campusflow.tickets import create_ticket
from campusflow.workflow.ticket_status import (
    update_ticket_status,
    reopen_ticket,
)
from campusflow.workflow.mentor_assignment import (
    assign_mentor_automatically,
    start_mentor_ticket,
    resolve_mentor_ticket,
)
from campusflow.workflow.event_store import (
    append_event,
    rebuild_tickets,
)


def create_new_ticket(
    filename,
    issuer,
    title,
    category,
    urgency,
    affected_users,
):
    if not isinstance(issuer, str) or not issuer.strip():
        raise ValueError("Fellow name or ID is required.")

    tickets = rebuild_tickets(filename)

    ticket = create_ticket(
        tickets,
        title,
        category,
        urgency,
        affected_users,
    )

    ticket["issuer"] = issuer.strip()

    append_event(
        filename,
        "ticket_created",
        ticket,
        issuer.strip(),
    )

    # Assignment is a second, separately recorded activity.
    mentor = assign_mentor_automatically(tickets, ticket)

    append_event(
        filename,
        "mentor_assigned",
        ticket,
        "system",
    )

    return deepcopy(ticket), mentor


def start_ticket(filename, ticket_id, mentor):
    tickets = rebuild_tickets(filename)

    result = start_mentor_ticket(
        tickets,
        ticket_id,
        mentor,
    )

    ticket = next(
        ticket for ticket in tickets
        if ticket["id"] == ticket_id
    )

    append_event(
        filename,
        "ticket_started",
        ticket,
        mentor,
    )

    return deepcopy(ticket)


def resolve_ticket(filename, ticket_id, mentor):
    tickets = rebuild_tickets(filename)

    resolve_mentor_ticket(tickets, ticket_id, mentor)

    ticket = next(
        ticket for ticket in tickets
        if ticket["id"] == ticket_id
    )

    append_event(
        filename,
        "ticket_resolved",
        ticket,
        mentor,
    )

    return deepcopy(ticket)


def reopen_existing_ticket(filename, ticket_id, mentor):
    tickets = rebuild_tickets(filename)

    ticket = next(
        (item for item in tickets if item["id"] == ticket_id),
        None,
    )

    if ticket is None:
        raise ValueError("Ticket not found.")

    if ticket.get("assigned_to") != mentor:
        raise ValueError(
            "You can only reopen your own tickets."
        )

    reopen_ticket(tickets, ticket_id)

    append_event(
        filename,
        "ticket_reopened",
        ticket,
        mentor,
    )

    return deepcopy(ticket)