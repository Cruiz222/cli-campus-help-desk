def validate_title(title):
    title = title.strip()
    if title == "":
        raise ValueError("Title can not be blank.")
    return title


