
import tempfile
import unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from campusflow_pro.application import ProApplication
from campusflow_pro.persistence.storage import load_state


class TestProApplication(unittest.TestCase):

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)

        self.path = Path(self.directory.name) / "state.json"

        self.now = datetime(
            2026, 10, 14, 10, 0,
            tzinfo=timezone.utc,
        )

        self.app = ProApplication(
            self.path,
            clock=lambda: self.now,
            input_fn=lambda prompt: "yes",
            output_fn=lambda message: None,
        )

    def create_ticket(self):
        return self.app.create(
            actor="admin",
            title="Network outage",
            category="Network",
            urgency="high",
            affected_users=20,
        )

    def test_new_application_has_empty_state(self):
        self.assertEqual(self.app.tickets(), [])
        self.assertEqual(self.app.events(), [])

    def test_create_generates_schema_v2_ticket(self):
        ticket = self.create_ticket()

        self.assertEqual(ticket["id"], "T001")
        self.assertEqual(ticket["priority"], "critical")
        self.assertEqual(ticket["escalation_cycle"], 0)
        self.assertIsNone(ticket["escalated_cycle"])
        self.assertIn("due_at", ticket)
        self.assertIn("updated_at", ticket)

    def test_create_persists_ticket_and_event(self):
        self.create_ticket()

        state = load_state(self.path)

        self.assertEqual(len(state["tickets"]), 1)
        self.assertEqual(len(state["events"]), 1)
        self.assertEqual(
            state["events"][0]["event_type"],
            "CREATE",
        )

    def test_create_survives_restart(self):
        self.create_ticket()

        restarted = ProApplication(
            self.path,
            clock=lambda: self.now,
        )

        self.assertEqual(len(restarted.tickets()), 1)
        self.assertEqual(len(restarted.events()), 1)

    def test_assignment_creates_audit_event(self):
        ticket = self.create_ticket()

        self.now += timedelta(minutes=5)

        updated = self.app.assign(
            "admin", ticket["id"], "Alice"
        )

        self.assertEqual(updated["assigned_to"], "Alice")
        self.assertEqual(
            self.app.events()[-1]["event_type"],
            "ASSIGN",
        )

    def test_cannot_start_unassigned_ticket(self):
        ticket = self.create_ticket()

        with self.assertRaises(ValueError):
            self.app.change_status(
                "admin", ticket["id"], "in_progress"
            )

        self.assertEqual(len(self.app.events()), 1)

    def test_start_and_resolve_lifecycle(self):
        ticket = self.create_ticket()
        self.app.assign("admin", ticket["id"], "Alice")

        self.now += timedelta(minutes=5)

        started = self.app.change_status(
            "admin", ticket["id"], "in_progress"
        )

        self.assertEqual(started["status"], "in_progress")
        self.assertIsNotNone(started["started_at"])

        self.now += timedelta(minutes=5)

        resolved = self.app.change_status(
            "admin", ticket["id"], "resolved"
        )

        self.assertEqual(resolved["status"], "resolved")
        self.assertIsNotNone(resolved["resolved_at"])

        event_types = [
            event["event_type"]
            for event in self.app.events()
        ]

        self.assertEqual(
            event_types,
            ["CREATE", "ASSIGN", "START", "RESOLVE"],
        )

    def test_reopen_starts_new_sla_cycle(self):
        ticket = self.create_ticket()
        self.app.assign("admin", ticket["id"], "Alice")
        self.app.change_status(
            "admin", ticket["id"], "in_progress"
        )
        self.app.change_status(
            "admin", ticket["id"], "resolved"
        )

        self.now += timedelta(hours=2)

        reopened = self.app.reopen(
            "admin", ticket["id"]
        )

        self.assertEqual(reopened["status"], "open")
        self.assertEqual(reopened["escalation_cycle"], 1)
        self.assertIsNone(reopened["escalated_cycle"])
        self.assertIsNone(reopened["resolved_at"])
        self.assertIsNone(reopened["started_at"])
        self.assertEqual(
            self.app.events()[-1]["event_type"],
            "REOPEN",
        )

    def test_overdue_ticket_escalates_once(self):
        ticket = self.create_ticket()

        self.now += timedelta(hours=2)

        first = self.app.escalate(now=self.now)
        second = self.app.escalate(now=self.now)

        self.assertEqual(first["newly_escalated"], 1)
        self.assertEqual(second["newly_escalated"], 0)
        self.assertEqual(second["already_escalated"], 1)

        escalation_events = [
            event
            for event in self.app.events()
            if event["event_type"] == "ESCALATE"
        ]

        self.assertEqual(len(escalation_events), 1)
        self.assertEqual(
            self.app.tickets()[0]["escalated_cycle"],
            0,
        )

    def test_ticket_ids_continue_after_restart(self):
        self.create_ticket()

        restarted = ProApplication(
            self.path,
            clock=lambda: self.now,
        )

        ticket = restarted.create(
            "admin",
            "Broken keyboard",
            "Hardware",
            "low",
            1,
        )

        self.assertEqual(ticket["id"], "T002")

    def test_failed_save_does_not_publish_state(self):
        original = deepcopy(self.app.state())

        with patch(
            "campusflow_pro.application.save_state",
            side_effect=OSError("Disk failure"),
        ):
            with self.assertRaises(OSError):
                self.create_ticket()

        self.assertEqual(self.app.state(), original)
        self.assertFalse(self.path.exists())

    def test_failed_assignment_save_rolls_back(self):
        ticket = self.create_ticket()
        original = deepcopy(self.app.state())

        with patch(
            "campusflow_pro.application.save_state",
            side_effect=OSError("Disk failure"),
        ):
            with self.assertRaises(OSError):
                self.app.assign(
                    "admin", ticket["id"], "Alice"
                )

        self.assertEqual(self.app.state(), original)
        self.assertEqual(load_state(self.path), original)

    def test_returned_ticket_cannot_mutate_state(self):
        ticket = self.create_ticket()
        ticket["title"] = "Tampered"

        self.assertEqual(
            self.app.tickets()[0]["title"],
            "Network outage",
        )

    def test_returned_state_cannot_mutate_internal_state(self):
        state = self.app.state()
        state["tickets"].append({"id": "FAKE"})

        self.assertEqual(len(self.app.tickets()), 0)

    def test_report_counts_tickets(self):
        self.create_ticket()

        report = self.app.report(now=self.now)

        self.assertEqual(report["total"], 1)

    def test_history_for_returns_ticket_events(self):
        ticket = self.create_ticket()
        self.app.assign("admin", ticket["id"], "Alice")

        history = self.app.history_for(ticket["id"])

        self.assertEqual(
            [event["event_type"] for event in history],
            ["CREATE", "ASSIGN"],
        )

    def test_escalation_remains_idempotent_after_restart(self):
        ticket = self.create_ticket()

        self.now += timedelta(hours=2)

        first = self.app.escalate(now=self.now)

        self.assertEqual(first["newly_escalated"], 1)

        restarted = ProApplication(
            self.path,
            clock=lambda: self.now,
        )

        second = restarted.escalate(now=self.now)

        self.assertEqual(second["newly_escalated"], 0)
        self.assertEqual(second["already_escalated"], 1)

        escalation_events = [
            event
            for event in restarted.events()
            if event["event_type"] == "ESCALATE"
        ]

        self.assertEqual(len(escalation_events), 1)
        self.assertEqual(
            restarted.tickets()[0]["escalated_cycle"],
            0,
        )

        self.assertEqual(
            load_state(self.path),
            restarted.state(),
        )

    def test_reopened_ticket_can_escalate_in_new_cycle(self):
        ticket = self.create_ticket()

        self.now += timedelta(hours=2)
        self.app.escalate(now=self.now)

        self.app.assign("admin", ticket["id"], "Alice")
        self.app.change_status(
            "admin", ticket["id"], "in_progress"
        )
        self.app.change_status(
            "admin", ticket["id"], "resolved"
        )

        self.now += timedelta(minutes=5)

        reopened = self.app.reopen(
            "admin", ticket["id"]
        )

        self.assertEqual(reopened["escalation_cycle"], 1)
        self.assertIsNone(reopened["escalated_cycle"])

        # A fresh cycle must not immediately escalate.
        early = self.app.escalate(now=self.now)

        self.assertEqual(early["newly_escalated"], 0)

        self.now += timedelta(hours=2)

        first = self.app.escalate(now=self.now)
        second = self.app.escalate(now=self.now)

        self.assertEqual(first["newly_escalated"], 1)
        self.assertEqual(second["newly_escalated"], 0)

        escalation_events = [
            event
            for event in self.app.events()
            if event["event_type"] == "ESCALATE"
        ]

        self.assertEqual(len(escalation_events), 2)

        self.assertEqual(
            [
                event["details"]["escalation_cycle"]
                for event in escalation_events
            ],
            [0, 1],
        )

        self.assertEqual(
            self.app.tickets()[0]["escalated_cycle"],
            1,
        )

    def test_reopened_escalation_survives_restart(self):
        ticket = self.create_ticket()

        self.now += timedelta(hours=2)
        self.app.escalate(now=self.now)

        self.app.assign("admin", ticket["id"], "Alice")
        self.app.change_status(
            "admin", ticket["id"], "in_progress"
        )
        self.app.change_status(
            "admin", ticket["id"], "resolved"
        )

        self.now += timedelta(minutes=5)
        self.app.reopen("admin", ticket["id"])

        self.now += timedelta(hours=2)
        self.app.escalate(now=self.now)

        restarted = ProApplication(
            self.path,
            clock=lambda: self.now,
        )

        result = restarted.escalate(now=self.now)

        self.assertEqual(result["newly_escalated"], 0)
        self.assertEqual(result["already_escalated"], 1)

        escalation_events = [
            event
            for event in restarted.events()
            if event["event_type"] == "ESCALATE"
        ]

        self.assertEqual(len(escalation_events), 2)

        self.assertEqual(
            restarted.tickets()[0]["escalation_cycle"],
            1,
        )
        self.assertEqual(
            restarted.tickets()[0]["escalated_cycle"],
            1,
        )

    def test_escalation_at_exact_deadline_is_not_triggered(self):
        ticket = self.create_ticket()

        due_at = datetime.fromisoformat(
            ticket["due_at"]
        )

        at_deadline = self.app.escalate(now=due_at)

        self.assertEqual(
            at_deadline["newly_escalated"],
            0,
        )

        after_deadline = self.app.escalate(
            now=due_at + timedelta(seconds=1)
        )

        self.assertEqual(
            after_deadline["newly_escalated"],
            1,
        )

        escalation_events = [
            event
            for event in self.app.events()
            if event["event_type"] == "ESCALATE"
        ]

        self.assertEqual(len(escalation_events), 1)


if __name__ == "__main__":
    unittest.main()
