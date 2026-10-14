
import unittest
from datetime import datetime, timezone

from campusflow_pro.sla.overdue import is_overdue


class TestOverdueDetection(unittest.TestCase):

    def setUp(self):
        self.ticket = {
            "id": "T001",
            "status": "open",
            "due_at": "2026-10-14T11:00:00+00:00",
        }

    def test_before_deadline_is_not_overdue(self):
        now = datetime(2026, 10, 14, 10, 59, tzinfo=timezone.utc)
        self.assertFalse(is_overdue(self.ticket, now))

    def test_exact_deadline_is_not_overdue(self):
        now = datetime(2026, 10, 14, 11, 0, tzinfo=timezone.utc)
        self.assertFalse(is_overdue(self.ticket, now))

    def test_after_deadline_is_overdue(self):
        now = datetime(2026, 10, 14, 11, 1, tzinfo=timezone.utc)
        self.assertTrue(is_overdue(self.ticket, now))

    def test_in_progress_ticket_can_be_overdue(self):
        self.ticket["status"] = "in_progress"
        now = datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc)
        self.assertTrue(is_overdue(self.ticket, now))

    def test_resolved_ticket_is_never_overdue(self):
        self.ticket["status"] = "resolved"
        now = datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc)
        self.assertFalse(is_overdue(self.ticket, now))

    def test_naive_now_is_rejected(self):
        now = datetime(2026, 10, 14, 12, 0)

        with self.assertRaises(ValueError):
            is_overdue(self.ticket, now)

    def test_invalid_due_at_is_rejected(self):
        self.ticket["due_at"] = "invalid"

        with self.assertRaises(ValueError):
            is_overdue(
                self.ticket,
                datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc),
            )

    def test_missing_due_at_is_rejected(self):
        del self.ticket["due_at"]

        with self.assertRaises(ValueError):
            is_overdue(
                self.ticket,
                datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc),
            )

    def test_invalid_status_is_rejected(self):
        self.ticket["status"] = "unknown"

        with self.assertRaises(ValueError):
            is_overdue(
                self.ticket,
                datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc),
            )


if __name__ == "__main__":
    unittest.main()
