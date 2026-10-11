from campusflow.tickets import current_timestamp


def update_ticket_status(tickets, ticket_id, new_status):

    valid_statuses = ("open", "in_progress", "resolved")

    if new_status not in valid_statuses:
        raise ValueError("Invalid ticket status")

    for ticket in tickets:

        if ticket["id"] == ticket_id:

            current_status = ticket["status"]

            if current_status == "resolved":
                raise ValueError(
                    "Resolved ticket cannot be modified"
                )

            if current_status == "open" and new_status == "in_progress":

                staff_name = ticket["assigned_to"]

                if not isinstance(staff_name, str) or not staff_name.strip():
                    raise ValueError(
                        "Ticket must be assigned before progressing"
                    )

                ticket["status"] = "in_progress"
                ticket["started_at"] = current_timestamp()
                return ticket

            if current_status == "in_progress" and new_status == "resolved":

                ticket["status"] = "resolved"
                ticket["resolved_at"] = current_timestamp()
                return ticket

            raise ValueError(
                f"Invalid transition: {current_status} -> {new_status}"
            )

    raise ValueError(f"Ticket {ticket_id} not found")



def reopen_ticket(tickets, ticket_id):

    for ticket in tickets:
        
        if ticket["id"] == ticket_id:

            current_status = ticket["status"]
    
            if current_status != "resolved":
                raise ValueError("only resolved tickets can be reopened")

            ticket["status"] = "open"
            ticket["resolved_at"] = None
            return ticket


    raise ValueError(f"Ticket {ticket_id} not found")