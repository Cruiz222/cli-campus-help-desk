"""Duplicate-ticket detection for CampusFlow Pro."""

import re

from campusflow_pro.ticket_fields import get_field

UNRESOLVED_STATUSES = {"open", "in_progress"}


def normalize_title(title):
    if not isinstance(title, str):
        raise ValueError("Ticket title must be a string.")
    return re.sub(r"\s+", " ", title.strip()).casefold()


def find_duplicates(new_ticket, existing_tickets):
    """Unresolved tickets with the same category and normalized title."""
    new_title = normalize_title(get_field(new_ticket, "title"))
    new_category = str(get_field(new_ticket, "category")).strip().casefold()

    matches = []
    for ticket in existing_tickets:
        if str(get_field(ticket, "status")).lower() not in UNRESOLVED_STATUSES:
            continue
        category = str(get_field(ticket, "category")).strip().casefold()
        if category != new_category:
            continue
        if normalize_title(get_field(ticket, "title")) == new_title:
            matches.append(ticket)
    return matches


def confirm_creation(new_ticket, existing_tickets, input_fn=input, output_fn=print):
    """Return True if creation should go ahead."""
    duplicates = find_duplicates(new_ticket, existing_tickets)
    if not duplicates:
        return True

    ids = ", ".join(str(get_field(t, "id")) for t in duplicates)
    output_fn(f"Warning: similar unresolved ticket(s) already exist: {ids}")
    answer = input_fn("Create anyway? (y/N): ").strip().lower()
    return answer in {"y", "yes"}