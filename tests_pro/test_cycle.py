
import unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone

from campusflow_pro.sla.cycle import reopen_sla_cycle


class TestReopenSLACycle(unittest.TestCase):

    def setUp(self):
        self.now = datetime(
            2026, 10, 14, 12, 0,
            tzinfo=timezone.utc,
        )

        self.ticket = {
            "id": "T001",
            "title": "Campus network outage",
            "category": "Network",
            "urgency": "high",
            "affected_users": 20,
            "priority": "critical",
            "status": "resolved",
            "assigned_to": "Mr Gabriel",
            "created_at": "2026-10-13T08:00:00+00:00",
            "updated_at": "2026-10-14T10:00:00+00:00",
            "started_at": "2026-10-13T09:00:00+00:00",
            "resolved_at": "2026-10-14T10:00:00+00:00",
            "due_at": "2026-10-13T09:00:00+00:00",
            "escalation_cycle": 0,
            "escalated_cycle": 0,
        }

    def test_reopening_changes_status_to_open(self):
        updated = reopen_sla_cycle(self.ticket, self.now)

        self.assertEqual(updated["status"], "open")

    def test_reopening_increments_cycle(self):
        updated = reopen_sla_cycle(self.ticket, self.now)

        self.assertEqual(updated["escalation_cycle"], 1)

    def test_reopening_resets_escalation_marker(self):
        updated = reopen_sla_cycle(self.ticket, self.now)

        self.assertIsNone(updated["escalated_cycle"])

    def test_reopening_recalculates_deadline(self):
        updated = reopen_sla_cycle(self.ticket, self.now)

        expected = self.now + timedelta(minutes=60)

        self.assertEqual(
            updated["due_at"],
            expected.isoformat(),
        )

    def test_reopening_updates_timestamp(self):
        updated = reopen_sla_cycle(self.ticket, self.now)

        self.assertEqual(
            updated["updated_at"],
            self.now.isoformat(),
        )

    def test_reopening_preserves_created_at(self):
        updated = reopen_sla_cycle(self.ticket, self.now)

        self.assertEqual(
            updated["created_at"],
            self.ticket["created_at"],
        )

    def test_reopening_preserves_ticket_identity(self):
        updated = reopen_sla_cycle(self.ticket, self.now)

        self.assertEqual(updated["id"], "T001")
        self.assertEqual(
            updated["title"],
            self.ticket["title"],
        )
        self.assertEqual(
            updated["assigned_to"],
            "Mr Gabriel",
        )

    def test_reopening_clears_resolution_timestamp(self):
        updated = reopen_sla_cycle(self.ticket, self.now)

        self.assertIsNone(updated["resolved_at"])

    def test_reopening_clears_started_timestamp(self):
        updated = reopen_sla_cycle(self.ticket, self.now)

        self.assertIsNone(updated["started_at"])

    def test_reopening_does_not_mutate_original(self):
        original = deepcopy(self.ticket)

        reopen_sla_cycle(self.ticket, self.now)

        self.assertEqual(self.ticket, original)

    def test_open_ticket_cannot_be_reopened(self):
        self.ticket["status"] = "open"

        with self.assertRaises(ValueError):
            reopen_sla_cycle(self.ticket, self.now)

    def test_in_progress_ticket_cannot_be_reopened(self):
        self.ticket["status"] = "in_progress"

        with self.assertRaises(ValueError):
            reopen_sla_cycle(self.ticket, self.now)

    def test_invalid_cycle_is_rejected(self):
        self.ticket["escalation_cycle"] = -1

        with self.assertRaises(ValueError):
            reopen_sla_cycle(self.ticket, self.now)

    def test_invalid_escalation_marker_is_rejected(self):
        self.ticket["escalated_cycle"] = 5

        with self.assertRaises(ValueError):
            reopen_sla_cycle(self.ticket, self.now)

    def test_naive_datetime_is_rejected(self):
        naive_now = datetime(2026, 10, 14, 12, 0)

        with self.assertRaises(ValueError):
            reopen_sla_cycle(self.ticket, naive_now)

    def test_unsupported_priority_is_rejected(self):
        self.ticket["priority"] = "urgent"

        with self.assertRaises(ValueError):
            reopen_sla_cycle(self.ticket, self.now)

    def test_reopening_from_later_cycle(self):
        self.ticket["escalation_cycle"] = 3
        self.ticket["escalated_cycle"] = 3

        updated = reopen_sla_cycle(self.ticket, self.now)

        self.assertEqual(updated["escalation_cycle"], 4)
        self.assertIsNone(updated["escalated_cycle"])

    def test_non_utc_datetime_is_normalized(self):
        local_timezone = timezone(timedelta(hours=1))

        local_now = datetime(
            2026, 10, 14, 13, 0,
            tzinfo=local_timezone,
        )

        updated = reopen_sla_cycle(self.ticket, local_now)

        self.assertEqual(
            updated["updated_at"],
            "2026-10-14T12:00:00+00:00",
        )
        self.assertEqual(
            updated["due_at"],
            "2026-10-14T13:00:00+00:00",
        )


if __name__ == "__main__":
    unittest.main()
