"""Read a field from a ticket that is either a dict or an object."""


def get_field(ticket, name, default=None):
    if isinstance(ticket, dict):
        return ticket.get(name, default)
    return getattr(ticket, name, default)