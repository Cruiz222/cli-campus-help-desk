def assign_ticket(tickets, ticket_id, staff_name):

    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name cannot be empty")

    for ticket in tickets:

        if ticket["id"] == ticket_id:

            if ticket["status"] == "resolved":
                raise ValueError("Ticket is already resolved")

            ticket["assigned_to"] = staff_name.strip()

            return ticket

    raise ValueError(f"Ticket {ticket_id} not found")