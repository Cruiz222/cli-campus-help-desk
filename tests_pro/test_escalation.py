from uuid import uuid4
import unittest
from copy import deepcopy
from datetime import datetime, timezone

from campusflow_pro.sla.escalation import escalate_overdue


class TestEscalation(unittest.TestCase):

    def setUp(self):
        self.now = datetime(
            2026, 10, 14, 12, 0,
            tzinfo=timezone.utc,
        )

        self.ticket = {
            "id": "T001",
            "status": "open",
            "priority": "critical",
            "due_at": "2026-10-14T11:00:00+00:00",
            "updated_at": "2026-10-14T10:00:00+00:00",
            "escalation_cycle": 0,
            "escalated_cycle": None,
        }

    @staticmethod
    def event_factory(**kwargs):
        return {
            "event_id": str(uuid4()),
            **kwargs,
        }

    def escalate(self, tickets, events=None):
        return escalate_overdue(
            tickets=tickets,
            events=[] if events is None else events,
            now=self.now,
            actor="Engineer A",
            event_factory=self.event_factory,
        )

    def test_overdue_ticket_is_escalated(self):
        result = self.escalate([self.ticket])

        self.assertEqual(result["newly_escalated"], 1)
        self.assertEqual(result["already_escalated"], 0)
        self.assertEqual(result["tickets"][0]["escalated_cycle"], 0)
        self.assertEqual(len(result["events"]), 1)
        self.assertEqual(result["events"][0]["event_type"], "ESCALATE")

    def test_escalation_preserves_status_priority_and_assignment(self):
        self.ticket["assigned_to"] = "Mr Gabriel"
        result = self.escalate([self.ticket])
        updated = result["tickets"][0]

        self.assertEqual(updated["status"], "open")
        self.assertEqual(updated["priority"], "critical")
        self.assertEqual(updated["assigned_to"], "Mr Gabriel")

    def test_repeated_escalation_does_not_create_another_event(self):
        first = self.escalate([self.ticket])

        second = self.escalate(
            first["tickets"],
            first["events"],
        )

        self.assertEqual(second["newly_escalated"], 0)
        self.assertEqual(second["already_escalated"], 1)
        self.assertEqual(len(second["events"]), 1)

    def test_not_overdue_ticket_is_not_escalated(self):
        self.ticket["due_at"] = "2026-10-14T13:00:00+00:00"

        result = self.escalate([self.ticket])

        self.assertEqual(result["newly_escalated"], 0)
        self.assertEqual(len(result["events"]), 0)

    def test_exact_deadline_is_not_escalated(self):
        self.ticket["due_at"] = self.now.isoformat()

        result = self.escalate([self.ticket])

        self.assertEqual(result["newly_escalated"], 0)

    def test_resolved_ticket_is_not_escalated(self):
        self.ticket["status"] = "resolved"

        result = self.escalate([self.ticket])

        self.assertEqual(result["newly_escalated"], 0)
        self.assertEqual(len(result["events"]), 0)

    def test_original_collections_are_not_mutated(self):
        tickets = [self.ticket]
        events = []
        original = deepcopy(tickets)

        self.escalate(tickets, events)

        self.assertEqual(tickets, original)
        self.assertEqual(events, [])

    def test_invalid_cycle_is_rejected(self):
        self.ticket["escalation_cycle"] = -1

        with self.assertRaises(ValueError):
            self.escalate([self.ticket])

    def test_invalid_actor_is_rejected(self):
        with self.assertRaises(ValueError):
            escalate_overdue(
                [self.ticket],
                [],
                now=self.now,
                actor=" ",
                event_factory=self.event_factory,
            )

    def test_reopened_cycle_can_escalate_again(self):
        previous_event = self.event_factory(
            event_type="ESCALATE",
            ticket_id="T001",
            actor="Engineer A",
            timestamp="2026-10-13T12:00:00+00:00",
            before_status="open",
            after_status="open",
            details={"escalation_cycle": 0},
        )

        self.ticket["escalation_cycle"] = 1
        self.ticket["escalated_cycle"] = None

        result = self.escalate(
            [self.ticket],
            [previous_event],
        )

        self.assertEqual(result["newly_escalated"], 1)
        self.assertEqual(len(result["events"]), 2)
        self.assertEqual(
            result["events"][-1]["details"]["escalation_cycle"],
            1,
        )


if __name__ == "__main__":
    unittest.main()
