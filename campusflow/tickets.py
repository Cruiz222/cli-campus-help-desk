from copy import deepcopy
VALID_CATEGORIES = ["Network", "Hardware", "Software", "Other"]
VALID_URGENCIES = ["low", "medium", "high"]
def validate_title(title):
    if not isinstance(title, str):
        raise ValueError("Title must be text.")
    title = title.strip()
    if title == "":
        raise ValueError("Title cannot be blank.")
    return title


def validate_category(categories, category):
    if not isinstance(category, str):
        raise ValueError("Category must be text.")
    category = category.strip()
    if category == "":
        raise ValueError("Category cannot be blank.")
    for each_category in categories:
        if each_category.lower() == category.lower():
            return each_category
    raise ValueError("Invalid category. Choose from: Network, Hardware, Software, Other.")


def validate_urgency(urgency_list, urgency):
    if not isinstance(urgency, str):
        raise ValueError("Urgency must be text.")
    urgency = urgency.strip()
    if urgency == "":
        raise ValueError("Urgency cannot be blank.") 
    if urgency.lower() not in urgency_list:
        raise ValueError("Invalid urgency. Choose from: low, medium or high.")
    return urgency.lower()

def validate_affected_users(affected_users):
    if isinstance(affected_users, bool):
        raise ValueError("Value of affected users must be an integer.")

    if not isinstance(affected_users, (str, int)):
        raise ValueError("Value of affected users must be an integer.")

    if isinstance(affected_users, str) and "." in affected_users:
        raise ValueError("Affected users cannot be a decimal/float.")

    try:
        affected_users = int(affected_users)
    except ValueError:
        raise ValueError("Affected users must be an integer.")

    if affected_users <= 0:
        raise ValueError("Affected users must be at least 1.")

    return affected_users

def calculate_priority(urgency, affected_users):
    if urgency == 'high' and affected_users >= 10:
        return 'critical'
    elif urgency == 'high' or affected_users >= 10:
        return 'high'
    elif urgency == 'medium' or affected_users >= 3:
        return 'medium'
    else:
        return 'low'

def generate_ticket_id(tickets):
    if not tickets:
        return "T001" 
    ticket_numbers = []
    for ticket in tickets:
        ticket_id_str = ticket["id"]
        numeric_part = int(ticket_id_str[1:]) #Remove the leading 'T' and convert the rest to an integer.
        ticket_numbers.append(numeric_part)
    largest_number = max(ticket_numbers)
    next_number = largest_number + 1
    return f"T{next_number:03d}"

def create_ticket(tickets, title, category, urgency, affected_users):
    title = validate_title(title)
    category = validate_category(VALID_CATEGORIES, category)
    urgency = validate_urgency(VALID_URGENCIES, urgency)
    affected_users = validate_affected_users(affected_users)
    priority = calculate_priority(urgency, affected_users)
    ticket_id = generate_ticket_id(tickets)
    new_ticket = {"id": ticket_id, "title": title, "category": category, "urgency": urgency, "affected_users": affected_users, "priority": priority, "status": "open", "assigned_to": None}
    tickets.append(new_ticket)
    return new_ticket


def get_ticket_by_id(tickets, ticket_id):
    """
    Finds and returns a specific ticket dictionary by its ID.
    Normalizes the ID with stripping and uppercase conversion.
    """
    if not isinstance(ticket_id, str):
        raise ValueError("Ticket ID must be text.")
    ticket_id = ticket_id.strip().upper()
    for ticket in tickets:
        if ticket.get('id') == ticket_id:
            return ticket
    raise ValueError(f"Ticket {ticket_id} not found.")

def list_tickets(tickets):
    """
    Returns a new list containing all tickets in order.
    Returns a copy to protect the original storage list from external mutation.
    """
    tickets_copy = deepcopy(tickets)
    return tickets_copy

