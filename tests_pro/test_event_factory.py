
import unittest
from datetime import datetime, timezone

from campusflow_pro.audit.factory import make_event


class TestEventFactory(unittest.TestCase):

    def setUp(self):
        self.timestamp = datetime(
            2026, 10, 14, 12, 0,
            tzinfo=timezone.utc,
        )

    def test_creates_string_event_id(self):
        event = make_event(
            event_type="CREATE",
            ticket_id="T001",
            actor="staff",
            timestamp=self.timestamp,
            after_status="open",
        )

        self.assertIsInstance(event["event_id"], str)
        self.assertTrue(event["event_id"])

    def test_event_ids_are_unique(self):
        events = [
            make_event(
                event_type="CREATE",
                ticket_id="T001",
                actor="staff",
                timestamp=self.timestamp,
            )
            for _ in range(20)
        ]

        self.assertEqual(
            len({event["event_id"] for event in events}),
            20,
        )

    def test_timestamp_is_utc(self):
        event = make_event(
            event_type="CREATE",
            ticket_id="T001",
            actor="staff",
            timestamp=self.timestamp,
        )

        self.assertEqual(
            event["timestamp"],
            "2026-10-14T12:00:00+00:00",
        )

    def test_rejects_naive_timestamp(self):
        with self.assertRaises(ValueError):
            make_event(
                event_type="CREATE",
                ticket_id="T001",
                actor="staff",
                timestamp=datetime(2026, 10, 14),
            )

    def test_escalation_event_has_required_details(self):
        event = make_event(
            event_type="ESCALATE",
            ticket_id="T001",
            actor="system",
            timestamp=self.timestamp.isoformat(),
            before_status="open",
            after_status="open",
            details={"escalation_cycle": 0},
        )

        self.assertEqual(event["event_type"], "ESCALATE")
        self.assertEqual(
            event["details"]["escalation_cycle"],
            0,
        )

    def test_normalizes_ticket_id(self):
        event = make_event(
            event_type="ASSIGN",
            ticket_id=" t001 ",
            actor="staff",
            timestamp=self.timestamp,
        )

        self.assertEqual(event["ticket_id"], "T001")


if __name__ == "__main__":
    unittest.main()
