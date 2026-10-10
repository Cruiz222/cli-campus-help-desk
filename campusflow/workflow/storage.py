import json


def save_tickets(tickets, filename):

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(tickets, file, indent=4)



import json


def save_tickets(tickets, filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(tickets, file, indent=4)


def load_tickets(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        return []

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in {filename}: {error}"
        ) from error