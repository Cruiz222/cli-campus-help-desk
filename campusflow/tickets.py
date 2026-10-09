VALID_CATEGORIES = ["Network", "Hardware", "Software", "Other"]
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



