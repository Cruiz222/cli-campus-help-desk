from pathlib import Path

from campusflow.tickets import create_ticket
from campusflow.workflow.ticket_status import reopen_ticket
from campusflow.workflow.reports import generate_report
from campusflow.workflow.storage import load_tickets, save_tickets

from campusflow.workflow.mentor_assignment import (
    MENTORS,
    assign_mentor_automatically,
    get_mentor_tickets,
    get_mentor_queue,
    start_mentor_ticket,
    resolve_mentor_ticket,
)


DATA_FILE = Path("tickets.json")


def display_tickets(tickets):
    if not tickets:
        print("\nNo tickets found.")
        return

    for ticket in tickets:
        print(f"\nTicket ID: {ticket['id']}")
        print(f"Title: {ticket['title']}")
        print(f"Issuer: {ticket.get('issuer', 'Unknown')}")
        print(f"Category: {ticket['category']}")
        print(f"Priority: {ticket['priority']}")
        print(f"Status: {ticket['status']}")
        print(f"Created: {ticket.get('created_at') or 'N/A'}")
        print(f"Started: {ticket.get('started_at') or 'Not yet'}")
        print(f"Resolved: {ticket.get('resolved_at') or 'Not yet'}")
        print(
            f"Assigned mentor: "
            f"{ticket.get('assigned_to') or 'Unassigned'}"
        )
        print("-" * 40)


def choose_mentor():
    print("\n========== SELECT MENTOR ==========")

    for index, mentor in enumerate(MENTORS, start=1):
        print(f"{index}. {mentor}")

    choice = input("Enter mentor number: ").strip()

    if not choice.isdigit():
        raise ValueError("Enter a valid mentor number.")

    index = int(choice) - 1

    if index < 0 or index >= len(MENTORS):
        raise ValueError("Invalid mentor selection.")

    return MENTORS[index]


def create_fellow_ticket(tickets, fellow_id):
    title = input("Ticket title: ")
    category = input(
        "Category (Network/Hardware/Software/Other): "
    )
    urgency = input("Urgency (low/medium/high): ")
    affected_users = input("Number of affected users: ")

    ticket = create_ticket(
        tickets,
        title,
        category,
        urgency,
        affected_users,
    )

    ticket["issuer"] = fellow_id

    mentor = assign_mentor_automatically(tickets, ticket)

    save_tickets(tickets, DATA_FILE)

    print(f"\nTicket {ticket['id']} created successfully.")
    print(f"Priority: {ticket['priority']}")
    print(f"Automatically assigned to: {mentor}")


def fellow_menu(tickets):
    fellow_id = input(
        "\nEnter your name or Fellow ID: "
    ).strip()

    if not fellow_id:
        print("A name or Fellow ID is required.")
        return

    while True:
        print("\n========== FELLOW MENU ==========")
        print("1. Create ticket")
        print("2. View my tickets")
        print("3. Check ticket status")
        print("4. Logout")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                create_fellow_ticket(tickets, fellow_id)

            elif choice == "2":
                my_tickets = [
                    ticket
                    for ticket in tickets
                    if ticket.get("issuer") == fellow_id
                ]

                display_tickets(my_tickets)

            elif choice == "3":
                ticket_id = input(
                    "Enter ticket ID: "
                ).strip().upper()

                ticket = next(
                    (
                        item
                        for item in tickets
                        if item["id"] == ticket_id
                        and item.get("issuer") == fellow_id
                    ),
                    None,
                )

                if ticket is None:
                    print("\nTicket not found in your records.")
                else:
                    display_tickets([ticket])

            elif choice == "4":
                return

            else:
                print("Invalid option.")

        except (ValueError, OSError) as error:
            print(f"\nError: {error}")


def mentor_menu(tickets):
    try:
        mentor = choose_mentor()
    except ValueError as error:
        print(f"\nError: {error}")
        return

    while True:
        print(f"\n========== {mentor.upper()} ==========")
        print("1. View my assigned tickets")
        print("2. View my pending queue")
        print("3. Start ticket")
        print("4. Resolve ticket")
        print("5. Reopen ticket")
        print("6. View report")
        print("7. Logout")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                display_tickets(
                    get_mentor_tickets(tickets, mentor)
                )

            elif choice == "2":
                display_tickets(
                    get_mentor_queue(tickets, mentor)
                )

            elif choice == "3":
                ticket_id = input(
                    "Ticket ID: "
                ).strip().upper()

                start_mentor_ticket(tickets, ticket_id, mentor)
                save_tickets(tickets, DATA_FILE)

                print("\nTicket started successfully.")

            elif choice == "4":
                ticket_id = input(
                    "Ticket ID: "
                ).strip().upper()

                resolve_mentor_ticket(tickets, ticket_id, mentor)
                save_tickets(tickets, DATA_FILE)

                print("\nTicket resolved successfully.")

            elif choice == "5":
                ticket_id = input(
                    "Ticket ID: "
                ).strip().upper()

                ticket = next(
                    (
                        item
                        for item in tickets
                        if item["id"] == ticket_id
                    ),
                    None,
                )

                if ticket is None:
                    raise ValueError("Ticket not found.")

                if ticket.get("assigned_to") != mentor:
                    raise ValueError(
                        "You can only reopen your own tickets."
                    )

                reopen_ticket(tickets, ticket_id)
                save_tickets(tickets, DATA_FILE)

                print("\nTicket reopened successfully.")

            elif choice == "6":
                report = generate_report(tickets)

                print("\n========== REPORT ==========")
                for key, value in report.items():
                    print(f"{key}: {value}")

            elif choice == "7":
                return

            else:
                print("Invalid option.")

        except (ValueError, OSError) as error:
            print(f"\nError: {error}")


def main():
    try:
        tickets = load_tickets(DATA_FILE)
    except (ValueError, OSError) as error:
        print(f"Unable to load tickets: {error}")
        return

    while True:
        print("\n========== CAMPUSFLOW ==========")
        print("1. Continue as Fellow")
        print("2. Continue as Mentor")
        print("3. Exit")

        choice = input("Choose your role: ").strip()

        if choice == "1":
            fellow_menu(tickets)

        elif choice == "2":
            mentor_menu(tickets)

        elif choice == "3":
            print("\nGoodbye!")
            break

        else:
            print("\nInvalid option.")


if __name__ == "__main__":
    main()