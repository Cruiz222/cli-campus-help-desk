
"""Transactional application service for CampusFlow Pro."""

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from campusflow.tickets import (
    VALID_CATEGORIES,
    VALID_URGENCIES,
    calculate_priority,
    validate_affected_users,
    validate_category,
    validate_title,
    validate_urgency,
)
from campusflow_pro.audit.factory import make_event
from campusflow_pro.duplicates import confirm_creation
from campusflow_pro.persistence.bootstrap import bootstrap_state
from campusflow_pro.persistence.schema import validate_document
from campusflow_pro.persistence.storage import save_state
from campusflow_pro.persistence.ticket_ids import next_ticket_id
from campusflow_pro.reports import build_report
from campusflow_pro.sla.attention_queue import attention_queue
from campusflow_pro.sla.cycle import reopen_sla_cycle
from campusflow_pro.sla.escalation import escalate_overdue
from campusflow_pro.sla.policy import calculate_due_at


class ProApplication:
    """
    Coordinate ticket operations and schema-v2 persistence.

    State is copied before modification and published only
    after a successful save.
    """

    def __init__(
        self,
        filename,
        clock=None,
        input_fn=input,
        output_fn=print,
    ):
        self.filename = Path(filename)
        self._clock = clock or (
            lambda: datetime.now(timezone.utc)
        )
        self._input = input_fn
        self._output = output_fn

        self._state = bootstrap_state(self.filename)

    def _now(self):
        now = self._clock()

        if not isinstance(now, datetime):
            raise TypeError("Clock must return a datetime")

        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("Clock must be timezone-aware")

        return now.astimezone(timezone.utc)

    @staticmethod
    def _actor(actor):
        if not isinstance(actor, str) or not actor.strip():
            raise ValueError("Actor must be a non-empty string")

        return actor.strip()

    @staticmethod
    def _ticket_id(ticket_id):
        if not isinstance(ticket_id, str):
            raise ValueError("Ticket ID must be text")

        ticket_id = ticket_id.strip().upper()

        if not ticket_id:
            raise ValueError("Ticket ID must not be empty")

        return ticket_id

    @staticmethod
    def _find_ticket(state, ticket_id):
        for ticket in state["tickets"]:
            if ticket["id"] == ticket_id:
                return ticket

        raise ValueError(f"Ticket {ticket_id} not found")

    def _commit(self, candidate):
        validate_document(candidate)
        save_state(candidate, self.filename)
        self._state = candidate

    def _record(
        self,
        state,
        *,
        event_type,
        ticket_id,
        actor,
        timestamp,
        before_status=None,
        after_status=None,
        details=None,
    ):
        event = make_event(
            event_type=event_type,
            ticket_id=ticket_id,
            actor=actor,
            timestamp=timestamp,
            before_status=before_status,
            after_status=after_status,
            details=details,
        )
        state["events"].append(event)
        return event

    def state(self):
        return deepcopy(self._state)

    def tickets(self):
        return deepcopy(self._state["tickets"])

    def events(self):
        return deepcopy(self._state["events"])

    def history_for(self, ticket_id):
        ticket_id = self._ticket_id(ticket_id)
        self._find_ticket(self._state, ticket_id)

        return deepcopy([
            event
            for event in self._state["events"]
            if event["ticket_id"] == ticket_id
        ])

    def create(
        self,
        actor,
        title,
        category,
        urgency,
        affected_users,
    ):
        actor = self._actor(actor)

        title = validate_title(title)
        category = validate_category(
            VALID_CATEGORIES, category
        )
        urgency = validate_urgency(
            VALID_URGENCIES, urgency
        )
        affected_users = validate_affected_users(
            affected_users
        )

        candidate = deepcopy(self._state)

        if not confirm_creation(
            {"title": title, "category": category},
            candidate["tickets"],
            self._input,
            self._output,
        ):
            return None

        now = self._now()
        timestamp = now.isoformat()
        priority = calculate_priority(
            urgency, affected_users
        )

        ticket = {
            "id": next_ticket_id(candidate["tickets"]),
            "title": title,
            "category": category,
            "urgency": urgency,
            "affected_users": affected_users,
            "priority": priority,
            "status": "open",
            "assigned_to": None,
            "created_at": timestamp,
            "updated_at": timestamp,
            "started_at": None,
            "resolved_at": None,
            "due_at": calculate_due_at(
                priority, now
            ).isoformat(),
            "escalation_cycle": 0,
            "escalated_cycle": None,
        }

        candidate["tickets"].append(ticket)

        self._record(
            candidate,
            event_type="CREATE",
            ticket_id=ticket["id"],
            actor=actor,
            timestamp=timestamp,
            after_status="open",
            details={
                "title": title,
                "priority": priority,
            },
        )

        self._commit(candidate)
        return deepcopy(ticket)

    def assign(self, actor, ticket_id, staff_name):
        actor = self._actor(actor)
        ticket_id = self._ticket_id(ticket_id)

        if not isinstance(staff_name, str) or not staff_name.strip():
            raise ValueError("Staff name cannot be empty")

        candidate = deepcopy(self._state)
        ticket = self._find_ticket(candidate, ticket_id)

        if ticket["status"] == "resolved":
            raise ValueError("Resolved ticket cannot be assigned")

        now = self._now().isoformat()

        ticket["assigned_to"] = staff_name.strip()
        ticket["updated_at"] = now

        self._record(
            candidate,
            event_type="ASSIGN",
            ticket_id=ticket_id,
            actor=actor,
            timestamp=now,
            before_status=ticket["status"],
            after_status=ticket["status"],
            details={"assigned_to": ticket["assigned_to"]},
        )

        self._commit(candidate)
        return deepcopy(ticket)

    def change_status(self, actor, ticket_id, new_status):
        actor = self._actor(actor)
        ticket_id = self._ticket_id(ticket_id)

        candidate = deepcopy(self._state)
        ticket = self._find_ticket(candidate, ticket_id)

        before = ticket["status"]
        now = self._now().isoformat()

        if before == "open" and new_status == "in_progress":
            if not ticket["assigned_to"]:
                raise ValueError(
                    "Ticket must be assigned before progressing"
                )

            ticket["status"] = "in_progress"
            ticket["started_at"] = now
            event_type = "START"

        elif before == "in_progress" and new_status == "resolved":
            ticket["status"] = "resolved"
            ticket["resolved_at"] = now
            event_type = "RESOLVE"

        else:
            raise ValueError(
                f"Invalid transition: {before} -> {new_status}"
            )

        ticket["updated_at"] = now

        self._record(
            candidate,
            event_type=event_type,
            ticket_id=ticket_id,
            actor=actor,
            timestamp=now,
            before_status=before,
            after_status=ticket["status"],
        )

        self._commit(candidate)
        return deepcopy(ticket)

    def reopen(self, actor, ticket_id):
        actor = self._actor(actor)
        ticket_id = self._ticket_id(ticket_id)

        candidate = deepcopy(self._state)
        original = self._find_ticket(candidate, ticket_id)

        now = self._now()
        updated = reopen_sla_cycle(original, now)

        index = candidate["tickets"].index(original)
        candidate["tickets"][index] = updated

        self._record(
            candidate,
            event_type="REOPEN",
            ticket_id=ticket_id,
            actor=actor,
            timestamp=now.isoformat(),
            before_status="resolved",
            after_status="open",
            details={
                "escalation_cycle": updated["escalation_cycle"]
            },
        )

        self._commit(candidate)
        return deepcopy(updated)

    def escalate(self, actor="system", now=None):
        actor = self._actor(actor)
        now = self._now() if now is None else now

        result = escalate_overdue(
            self._state["tickets"],
            self._state["events"],
            now=now,
            actor=actor,
            event_factory=make_event,
        )

        if result["newly_escalated"] == 0:
            return {
                "newly_escalated": 0,
                "already_escalated": result["already_escalated"],
            }

        candidate = {
            "schema_version": 2,
            "tickets": result["tickets"],
            "events": result["events"],
        }

        self._commit(candidate)

        return {
            "newly_escalated": result["newly_escalated"],
            "already_escalated": result["already_escalated"],
        }

    def attention_queue(self, now=None):
        return attention_queue(
            self.tickets(),
            now=now,
        )

    def report(self, now=None):
        return build_report(
            self.tickets(),
            now=now,
        )
