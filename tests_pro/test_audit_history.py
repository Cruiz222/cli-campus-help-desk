import unittest
from datetime import datetime, timezone, timedelta

from campusflow_pro.audit.history import AuditHistory


class TestAuditHistory(unittest.TestCase):

    def setUp(self):
        self.history = AuditHistory()

    def test_record_create_event(self):
        event = self.history.record(
            ticket_id=1,
            event_type="CREATE",
            actor="Fellow",
            after_status="open",
        )

        self.assertEqual(event["ticket_id"], 1)
        self.assertEqual(event["event_type"], "CREATE")
        self.assertEqual(event["after_status"], "open")
        self.assertEqual(self.history.count(), 1)

    def test_empty_actor_is_rejected(self):
        with self.assertRaises(ValueError):
            self.history.record(
                ticket_id=1,
                event_type="CREATE",
                actor=" ",
            )

        self.assertEqual(self.history.count(), 0)

    def test_invalid_event_is_rejected(self):
        with self.assertRaises(ValueError):
            self.history.record(
                ticket_id=1,
                event_type="DELETE",
                actor="Fellow",
            )

        self.assertEqual(self.history.count(), 0)

    def test_events_are_ordered_by_timestamp(self):
        times = iter([
            datetime(2026, 10, 14, 10, 2, tzinfo=timezone.utc),
            datetime(2026, 10, 14, 10, 1, tzinfo=timezone.utc),
        ])

        history = AuditHistory(clock=lambda: next(times))

        history.record(1, "CREATE", "Fellow")
        history.record(1, "ASSIGN", "Mentor")

        events = history.for_ticket(1)

        self.assertEqual(events[0]["event_type"], "ASSIGN")
        self.assertEqual(events[1]["event_type"], "CREATE")

    def test_returned_event_cannot_modify_stored_event(self):
        event = self.history.record(
            ticket_id=1,
            event_type="CREATE",
            actor="Fellow",
        )

        event["actor"] = "Changed"

        stored_event = self.history.for_ticket(1)[0]
        self.assertEqual(stored_event["actor"], "Fellow")

    def test_timezone_naive_timestamp_is_rejected(self):
        history = AuditHistory(
            clock=lambda: datetime(2026, 10, 14, 10, 0)
        )

        with self.assertRaises(ValueError):
            history.record(1, "CREATE", "Fellow")

        self.assertEqual(history.count(), 0)


if __name__ == "__main__":
    unittest.main()