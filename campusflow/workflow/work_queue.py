def get_work_queue(tickets):

    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    open_tickets = [
        ticket for ticket in tickets
        if ticket["status"] == "open"
    ]

    def sort_key(ticket):
        priority_rank = priority_order[ticket["priority"]]
        numeric_id = int(ticket["id"][1:])

        return priority_rank, numeric_id

    sorted_list = sorted(open_tickets, key=sort_key)

    return sorted_list