
"""Interactive CLI for CampusFlow Pro."""

from pathlib import Path

from campusflow_pro.application import ProApplication
from campusflow_pro.knowledge_quiz import run_quiz


DATA_FILE = Path("campusflow_pro.json")


def display_tickets(tickets, output_fn=print):
    """Display tickets in a readable format."""

    if not tickets:
        output_fn("\nNo tickets found.")
        return

    for ticket in tickets:
        output_fn(f"\nTicket ID: {ticket['id']}")
        output_fn(f"Title: {ticket['title']}")
        output_fn(f"Category: {ticket['category']}")
        output_fn(f"Priority: {ticket['priority']}")
        output_fn(f"Status: {ticket['status']}")
        output_fn(
            f"Assigned to: "
            f"{ticket['assigned_to'] or 'Unassigned'}"
        )
        output_fn(f"Created: {ticket['created_at']}")
        output_fn(f"Updated: {ticket['updated_at']}")
        output_fn(f"SLA deadline: {ticket['due_at']}")
        output_fn(
            f"SLA cycle: {ticket['escalation_cycle']}"
        )
        output_fn("-" * 40)


def display_history(events, output_fn=print):
    """Display audit history for a ticket."""

    if not events:
        output_fn("\nNo audit events found.")
        return

    for event in events:
        output_fn(
            f"\n{event['timestamp']} | "
            f"{event['event_type']} | "
            f"Actor: {event['actor']}"
        )
        output_fn(
            f"Status: {event['before_status']} "
            f"-> {event['after_status']}"
        )

        if event["details"]:
            output_fn(f"Details: {event['details']}")


def display_attention_queue(items, output_fn=print):
    """Display tickets requiring SLA attention."""

    if not items:
        output_fn(
            "\nNo tickets currently require SLA attention."
        )
        return

    for item in items:
        ticket = item["ticket"]

        output_fn(
            f"\n{ticket['id']} | "
            f"{ticket['title']} | "
            f"{item['state'].upper()}"
        )
        output_fn(f"Priority: {item['priority']}")
        output_fn(f"Deadline: {item['deadline']}")
        output_fn(f"Remaining: {item['remaining']}")


def display_report(report, output_fn=print):
    """Display CampusFlow Pro summary metrics."""

    output_fn(
        "\n========== CAMPUSFLOW PRO REPORT =========="
    )

    for key, value in report.items():
        output_fn(f"{key}: {value}")


def run_cli(
    app,
    input_fn=input,
    output_fn=print,
):
    """Run the interactive CampusFlow Pro CLI."""

    while True:
        try:
            output_fn(
                "\n========== CAMPUSFLOW PRO =========="
            )
            output_fn("1. Create ticket")
            output_fn("2. View all tickets")
            output_fn("3. Assign ticket")
            output_fn("4. Start ticket")
            output_fn("5. Resolve ticket")
            output_fn("6. Reopen ticket")
            output_fn("7. View ticket history")
            output_fn("8. View SLA attention queue")
            output_fn("9. Escalate overdue tickets")
            output_fn("10. View report")
            output_fn("11. Engineer Knowledge Quiz")
            output_fn("12. Exit")

            choice = input_fn(
                "Choose an option: "
            ).strip()

            if choice == "1":
                actor = input_fn(
                    "Your name or ID: "
                )
                title = input_fn(
                    "Ticket title: "
                )
                category = input_fn(
                    "Category (Network/Hardware/Software/Other): "
                )
                urgency = input_fn(
                    "Urgency (low/medium/high): "
                )
                affected_users = input_fn(
                    "Number of affected users: "
                )

                ticket = app.create(
                    actor,
                    title,
                    category,
                    urgency,
                    affected_users,
                )

                if ticket is None:
                    output_fn(
                        "\nTicket creation cancelled."
                    )
                else:
                    output_fn(
                        f"\nTicket {ticket['id']} "
                        f"created successfully."
                    )
                    output_fn(
                        f"Priority: {ticket['priority']}"
                    )
                    output_fn(
                        f"SLA deadline: {ticket['due_at']}"
                    )

            elif choice == "2":
                display_tickets(
                    app.tickets(),
                    output_fn,
                )

            elif choice == "3":
                actor = input_fn(
                    "Your name or ID: "
                )
                ticket_id = input_fn(
                    "Ticket ID: "
                )
                staff_name = input_fn(
                    "Assign to: "
                )

                app.assign(
                    actor,
                    ticket_id,
                    staff_name,
                )

                output_fn(
                    "\nTicket assigned successfully."
                )

            elif choice == "4":
                actor = input_fn(
                    "Your name or ID: "
                )
                ticket_id = input_fn(
                    "Ticket ID: "
                )

                app.change_status(
                    actor,
                    ticket_id,
                    "in_progress",
                )

                output_fn(
                    "\nTicket started successfully."
                )

            elif choice == "5":
                actor = input_fn(
                    "Your name or ID: "
                )
                ticket_id = input_fn(
                    "Ticket ID: "
                )

                app.change_status(
                    actor,
                    ticket_id,
                    "resolved",
                )

                output_fn(
                    "\nTicket resolved successfully."
                )

            elif choice == "6":
                actor = input_fn(
                    "Your name or ID: "
                )
                ticket_id = input_fn(
                    "Ticket ID: "
                )

                app.reopen(
                    actor,
                    ticket_id,
                )

                output_fn(
                    "\nTicket reopened successfully."
                )

            elif choice == "7":
                ticket_id = input_fn(
                    "Ticket ID: "
                )

                display_history(
                    app.history_for(ticket_id),
                    output_fn,
                )

            elif choice == "8":
                display_attention_queue(
                    app.attention_queue(),
                    output_fn,
                )

            elif choice == "9":
                actor = input_fn(
                    "Your name or ID: "
                )

                result = app.escalate(
                    actor=actor
                )

                output_fn(
                    f"\nNew escalations: "
                    f"{result['newly_escalated']}"
                )
                output_fn(
                    f"Already escalated: "
                    f"{result['already_escalated']}"
                )

            elif choice == "10":
                display_report(
                    app.report(),
                    output_fn,
                )

            elif choice == "11":
                run_quiz(
                    input_fn=input_fn,
                    output_fn=output_fn,
                )

            elif choice == "12":
                output_fn("\nGoodbye!")
                return

            else:
                output_fn("\nInvalid option.")

        except KeyboardInterrupt:
            output_fn(
                "\n\nOperation cancelled. "
                "Returning to the main menu."
            )
            continue

        except EOFError:
            output_fn(
                "\nInput closed. Goodbye!"
            )
            return

        except (ValueError, TypeError) as error:
            output_fn(f"\nError: {error}")

        except OSError as error:
            output_fn(
                f"\nStorage or system error: {error}"
            )
            output_fn(
                "The operation could not be completed. "
                "Check the storage file and permissions."
            )


def main():
    """Start CampusFlow Pro."""

    try:
        app = ProApplication(DATA_FILE)

    except KeyboardInterrupt:
        print("\nStartup cancelled.")
        return

    except (ValueError, TypeError, OSError) as error:
        print(
            f"Unable to load CampusFlow Pro state: "
            f"{error}"
        )
        return

    run_cli(app)


if __name__ == "__main__":
    main()
