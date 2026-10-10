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
    if "." in str(affected_users):
        raise ValueError("Affected users cannot be a decimal/float.")
    try:
        affected_users = int(affected_users)
    except ValueError:
        raise ValueError("Affected users must be an integer.")
    if affected_users <= 0:
        raise ValueError("Affected users must be at least 1.")
    return affected_users

#print(validate_affected_users(2.5))


