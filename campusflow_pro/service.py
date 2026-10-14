"""Wires audit history and duplicate detection around the original workflow."""

from campusflow.tickets import create_ticket, get_ticket_by_id
from campusflow.workflow.assign_ticket import assign_ticket
from campusflow.workflow.ticket_status import update_ticket_status, reopen_ticket
from campusflow_pro.audit.history import AuditHistory
from campusflow_pro.duplicates import confirm_creation
from campusflow_pro.reports import build_report
from campusflow_pro.sla.attention_queue import attention_queue


def _norm(ticket_id):
    return ticket_id.strip().upper() if isinstance(ticket_id, str) else ticket_id


class TicketService:

    def __init__(self, tickets=None, history=None, input_fn=input, output_fn=print):
        self.tickets = tickets if tickets is not None else []
        self.history = history or AuditHistory()
        self._input = input_fn
        self._output = output_fn

    def create(self, actor, title, category, urgency, affected_users):
        """Returns the new ticket, or None if the user declined a duplicate."""
        candidate = {"title": title, "category": category}
        if not confirm_creation(candidate, self.tickets, self._input, self._output):
            return None
        ticket = create_ticket(self.tickets, title, category, urgency, affected_users)
        self.history.record(
            ticket["id"], "CREATE", actor,
            after_status=ticket["status"],
            details={"title": ticket["title"], "priority": ticket["priority"]},
        )
        return ticket

    def assign(self, actor, ticket_id, staff_name):
        ticket_id = _norm(ticket_id)
        ticket = assign_ticket(self.tickets, ticket_id, staff_name)
        self.history.record(
            ticket_id, "ASSIGN", actor,
            before_status=ticket["status"], after_status=ticket["status"],
            details={"assigned_to": ticket["assigned_to"]},
        )
        return ticket

    def change_status(self, actor, ticket_id, new_status):
        ticket_id = _norm(ticket_id)
        before = get_ticket_by_id(self.tickets, ticket_id)["status"]
        ticket = update_ticket_status(self.tickets, ticket_id, new_status)
        event = "START" if ticket["status"] == "in_progress" else "RESOLVE"
        self.history.record(
            ticket_id, event, actor,
            before_status=before, after_status=ticket["status"],
        )
        return ticket

    def reopen(self, actor, ticket_id):
        ticket_id = _norm(ticket_id)
        before = get_ticket_by_id(self.tickets, ticket_id)["status"]
        ticket = reopen_ticket(self.tickets, ticket_id)
        self.history.record(
            ticket_id, "REOPEN", actor,
            before_status=before, after_status=ticket["status"],
        )
        return ticket

    def attention_queue(self, now=None):
        return attention_queue(self.tickets, now)

    def report(self, now=None):
        return build_report(self.tickets, now)