from pathlib import Path

from campusflow.tickets import create_ticket, list_tickets
from campusflow.workflow.assign_ticket import assign_ticket
from campusflow.workflow.ticket_status import (
    update_ticket_status,
    reopen_ticket,
)
from campusflow.workflow.work_queue import get_work_queue
from campusflow.workflow.reports import generate_report
from campusflow.workflow.storage import save_tickets, load_tickets


DATA_FILE = Path("tickets.json")


def display_tickets(tickets):
    if not tickets:
        print("\nNo tickets found.")
        return

    for ticket in tickets:
        print(
            f"\nID: {ticket['id']}"
            f"\nTitle: {ticket['title']}"
            f"\nCategory: {ticket['category']}"
            f"\nPriority: {ticket['priority']}"
            f"\nStatus: {ticket['status']}"
            f"\nAssigned to: {ticket['assigned_to'] or 'Unassigned'}"
        )


def show_menu():
    print("\n========== CAMPUSFLOW ==========")
    print("1. Create ticket")
    print("2. List tickets")
    print("3. Assign ticket")
    print("4. Start ticket")
    print("5. Resolve ticket")
    print("6. Reopen ticket")
    print("7. View work queue")
    print("8. View report")
    print("9. Exit")
    print("================================")


def main():
    try:
        tickets = load_tickets(DATA_FILE)
    except (ValueError, OSError) as error:
        print(f"Unable to load tickets: {error}")
        return

    while True:
        show_menu()
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                title = input("Ticket title: ")
                category = input(
                    "Category (Network/Hardware/Software/Other): "
                )
                urgency = input(
                    "Urgency (low/medium/high): "
                )
                affected_users = input("Affected users: ")

                ticket = create_ticket(
                    tickets,
                    title,
                    category,
                    urgency,
                    affected_users,
                )

                save_tickets(tickets, DATA_FILE)
                print(f"\nTicket {ticket['id']} created successfully.")

            elif choice == "2":
                display_tickets(list_tickets(tickets))

            elif choice == "3":
                ticket_id = input("Ticket ID: ").strip()
                staff = input("Staff name: ").strip()

                assign_ticket(tickets, ticket_id, staff)
                save_tickets(tickets, DATA_FILE)
                print("\nTicket assigned successfully.")

            elif choice == "4":
                ticket_id = input("Ticket ID: ").strip()

                update_ticket_status(
                    tickets,
                    ticket_id,
                    "in_progress",
                )

                save_tickets(tickets, DATA_FILE)
                print("\nTicket moved to in_progress.")

            elif choice == "5":
                ticket_id = input("Ticket ID: ").strip()

                update_ticket_status(
                    tickets,
                    ticket_id,
                    "resolved",
                )

                save_tickets(tickets, DATA_FILE)
                print("\nTicket resolved successfully.")

            elif choice == "6":
                ticket_id = input("Ticket ID: ").strip()

                reopen_ticket(tickets, ticket_id)
                save_tickets(tickets, DATA_FILE)
                print("\nTicket reopened successfully.")

            elif choice == "7":
                display_tickets(get_work_queue(tickets))

            elif choice == "8":
                report = generate_report(tickets)

                print("\n========== REPORT ==========")
                for key, value in report.items():
                    print(f"{key}: {value}")

            elif choice == "9":
                print("\nThank you for using CampusFlow!")
                break

            else:
                print("\nInvalid option. Choose 1-9.")

        except ValueError as error:
            print(f"\nError: {error}")

        except OSError as error:
            print(f"\nStorage error: {error}")
            print("Your latest changes may not have been saved.")


if __name__ == "__main__":
    main()