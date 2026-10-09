VALID_CATEGORIES = ["Network", "Hardware", "Software", "Other"]
def validate_title(title):
    if not isinstance(title, str):
        raise ValueError("Title must be text.")
    title = title.strip()
    if title == "":
        raise ValueError("Title cannot be blank.")
    return title



