
from pathlib import Path

from campusflow.workflow.event_store import (
    rebuild_tickets,
    get_ticket_history,
)

from campusflow.workflow.ticket_commands import (
    create_new_ticket,
    start_ticket,
    resolve_ticket,
    reopen_existing_ticket,
)

from campusflow.workflow.mentor_assignment import (
    MENTORS,
    get_mentor_tickets,
    get_mentor_queue,
)

from campusflow.workflow.reports import generate_report


DATA_FILE = Path("ticket_events.jsonl")


# --------------------------------------------------
# DISPLAY HELPERS
# --------------------------------------------------

def display_ticket(ticket):
    print("\n" + "-" * 50)
    print(f"Ticket ID:       {ticket['id']}")
    print(f"Title:           {ticket['title']}")
    print(f"Issuer:          {ticket.get('issuer', 'Unknown')}")
    print(f"Category:        {ticket['category']}")
    print(f"Urgency:         {ticket['urgency']}")
    print(f"Affected users:  {ticket['affected_users']}")
    print(f"Priority:        {ticket['priority']}")
    print(f"Status:          {ticket['status']}")
    print(
        f"Assigned mentor: {ticket.get('assigned_to') or 'Unassigned'}"
    )
    print(f"Created at:      {ticket.get('created_at') or 'N/A'}")
    print(f"Resolved at:     {ticket.get('resolved_at') or 'N/A'}")
    print("-" * 50)


def display_tickets(tickets):
    if not tickets:
        print("\nNo tickets found.")
        return

    print(f"\nTotal tickets: {len(tickets)}")

    for ticket in tickets:
        display_ticket(ticket)


def display_history(events):
    if not events:
        print("\nNo activity history found.")
        return

    print("\n========== TICKET ACTIVITY HISTORY ==========")

    for index, event in enumerate(events, start=1):
        print(f"\nActivity #{index}")
        print(f"Event ID:   {event['event_id']}")
        print(f"Activity:   {event['event_type']}")
        print(f"Performed:  {event['actor']}")
        print(f"Timestamp:  {event['occurred_at']}")

        snapshot = event["ticket_snapshot"]

        print(f"Status:     {snapshot.get('status')}")
        print(
            f"Mentor:     "
            f"{snapshot.get('assigned_to') or 'Unassigned'}"
        )


# --------------------------------------------------
# STORAGE HELPERS
# --------------------------------------------------

def load_current_tickets():
    return rebuild_tickets(DATA_FILE)


def find_ticket(tickets, ticket_id):
    ticket_id = ticket_id.strip().upper()

    return next(
        (
            ticket
            for ticket in tickets
            if ticket["id"].upper() == ticket_id
        ),
        None,
    )


def normalize_ticket_id():
    return input("Enter ticket ID: ").strip().upper()


def get_fellow_ticket(tickets, ticket_id, fellow_id):
    ticket = find_ticket(tickets, ticket_id)

    if ticket is None:
        raise ValueError("Ticket not found.")

    if ticket.get("issuer") != fellow_id:
        raise ValueError(
            "This ticket does not belong to your Fellow ID."
        )

    return ticket


def get_owned_mentor_ticket(tickets, ticket_id, mentor):
    ticket = find_ticket(tickets, ticket_id)

    if ticket is None:
        raise ValueError("Ticket not found.")

    if ticket.get("assigned_to") != mentor:
        raise ValueError(
            "This ticket is not assigned to you."
        )

    return ticket


# --------------------------------------------------
# FELLOW OPERATIONS
# --------------------------------------------------

def fellow_create_ticket(fellow_id):
    print("\n========== CREATE TICKET ==========")

    title = input("Ticket title: ").strip()
    category = input(
        "Category (Network/Hardware/Software/Other): "
    ).strip()
    urgency = input(
        "Urgency (low/medium/high): "
    ).strip()
    affected_users = input(
        "Number of affected users: "
    ).strip()

    ticket, mentor = create_new_ticket(
        DATA_FILE,
        fellow_id,
        title,
        category,
        urgency,
        affected_users,
    )

    print("\nTicket created successfully!")
    print(f"Ticket ID: {ticket['id']}")
    print(f"Priority: {ticket['priority']}")
    print(f"Assigned mentor: {mentor}")
    print(f"Current status: {ticket['status']}")


def fellow_view_tickets(fellow_id):
    tickets = load_current_tickets()

    my_tickets = [
        ticket
        for ticket in tickets
        if ticket.get("issuer") == fellow_id
    ]

    display_tickets(my_tickets)


def fellow_check_status(fellow_id):
    tickets = load_current_tickets()
    ticket_id = normalize_ticket_id()

    ticket = get_fellow_ticket(
        tickets,
        ticket_id,
        fellow_id,
    )

    display_ticket(ticket)


def fellow_view_history(fellow_id):
    tickets = load_current_tickets()
    ticket_id = normalize_ticket_id()

    get_fellow_ticket(
        tickets,
        ticket_id,
        fellow_id,
    )

    events = get_ticket_history(
        DATA_FILE,
        ticket_id,
    )

    display_history(events)


def fellow_menu():
    print("\n========== FELLOW IDENTIFICATION ==========")

    fellow_id = input(
        "Enter your Fellow ID or full name: "
    ).strip()

    if not fellow_id:
        print("\nFellow ID or name is required.")
        return

    while True:
        print("\n========== FELLOW MENU ==========")
        print(f"Fellow: {fellow_id}")
        print("1. Create ticket")
        print("2. View my tickets")
        print("3. Check ticket status")
        print("4. View ticket activity history")
        print("5. Logout")

        choice = input("\nChoose an option: ").strip()

        try:
            if choice == "1":
                fellow_create_ticket(fellow_id)

            elif choice == "2":
                fellow_view_tickets(fellow_id)

            elif choice == "3":
                fellow_check_status(fellow_id)

            elif choice == "4":
                fellow_view_history(fellow_id)

            elif choice == "5":
                print("\nLogged out successfully.")
                return

            else:
                print("\nInvalid option.")

        except (ValueError, OSError) as error:
            print(f"\nError: {error}")


# --------------------------------------------------
# MENTOR IDENTIFICATION
# --------------------------------------------------

def choose_mentor():
    print("\n========== SELECT MENTOR ==========")

    for index, mentor in enumerate(MENTORS, start=1):
        print(f"{index}. {mentor}")

    choice = input("\nEnter mentor number: ").strip()

    if not choice.isdigit():
        raise ValueError("Enter a valid mentor number.")

    index = int(choice) - 1

    if index < 0 or index >= len(MENTORS):
        raise ValueError("Invalid mentor selection.")

    return MENTORS[index]


# --------------------------------------------------
# MENTOR OPERATIONS
# --------------------------------------------------

def mentor_view_assigned_tickets(mentor):
    tickets = load_current_tickets()

    assigned = get_mentor_tickets(
        tickets,
        mentor,
    )

    display_tickets(assigned)


def mentor_view_queue(mentor):
    tickets = load_current_tickets()

    queue = get_mentor_queue(
        tickets,
        mentor,
    )

    display_tickets(queue)


def mentor_start_ticket(mentor):
    ticket_id = normalize_ticket_id()

    ticket = start_ticket(
        DATA_FILE,
        ticket_id,
        mentor,
    )

    print("\nTicket started successfully.")
    display_ticket(ticket)


def mentor_resolve_ticket(mentor):
    ticket_id = normalize_ticket_id()

    ticket = resolve_ticket(
        DATA_FILE,
        ticket_id,
        mentor,
    )

    print("\nTicket resolved successfully.")
    display_ticket(ticket)


def mentor_reopen_ticket(mentor):
    ticket_id = normalize_ticket_id()

    ticket = reopen_existing_ticket(
        DATA_FILE,
        ticket_id,
        mentor,
    )

    print("\nTicket reopened successfully.")
    display_ticket(ticket)


def mentor_view_history(mentor):
    tickets = load_current_tickets()
    ticket_id = normalize_ticket_id()

    get_owned_mentor_ticket(
        tickets,
        ticket_id,
        mentor,
    )

    events = get_ticket_history(
        DATA_FILE,
        ticket_id,
    )

    display_history(events)


def mentor_view_report():
    tickets = load_current_tickets()

    report = generate_report(tickets)

    print("\n========== CAMPUSFLOW REPORT ==========")

    for key, value in report.items():
        print(f"{key}: {value}")


def mentor_menu():
    try:
        mentor = choose_mentor()
    except ValueError as error:
        print(f"\nError: {error}")
        return

    while True:
        print("\n========== MENTOR MENU ==========")
        print(f"Mentor: {mentor}")
        print("1. View my assigned tickets")
        print("2. View my pending queue")
        print("3. Start ticket")
        print("4. Resolve ticket")
        print("5. Reopen ticket")
        print("6. View ticket activity history")
        print("7. View overall report")
        print("8. Logout")

        choice = input("\nChoose an option: ").strip()

        try:
            if choice == "1":
                mentor_view_assigned_tickets(mentor)

            elif choice == "2":
                mentor_view_queue(mentor)

            elif choice == "3":
                mentor_start_ticket(mentor)

            elif choice == "4":
                mentor_resolve_ticket(mentor)

            elif choice == "5":
                mentor_reopen_ticket(mentor)

            elif choice == "6":
                mentor_view_history(mentor)

            elif choice == "7":
                mentor_view_report()

            elif choice == "8":
                print("\nLogged out successfully.")
                return

            else:
                print("\nInvalid option.")

        except (ValueError, OSError) as error:
            print(f"\nError: {error}")


# --------------------------------------------------
# APPLICATION ENTRY POINT
# --------------------------------------------------

def main():
    print("\nWelcome to CampusFlow Help Desk")

    try:
        load_current_tickets()
    except (ValueError, OSError) as error:
        print(f"\nUnable to load ticket history: {error}")
        return

    while True:
        print("\n========== CAMPUSFLOW ==========")
        print("1. Continue as Fellow")
        print("2. Continue as Mentor")
        print("3. Exit")

        choice = input("\nChoose your role: ").strip()

        if choice == "1":
            fellow_menu()

        elif choice == "2":
            mentor_menu()

        elif choice == "3":
            print("\nThank you for using CampusFlow.")
            return

        else:
            print("\nInvalid option.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nCampusFlow closed.")
