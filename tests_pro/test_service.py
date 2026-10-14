import unittest
from datetime import datetime, timedelta

from campusflow_pro.service import TicketService


def quiet(answer="n"):
    return TicketService(input_fn=lambda _: answer, output_fn=lambda _: None)


class TestTicketService(unittest.TestCase):

    def test_create_records_event(self):
        s = quiet()
        t = s.create("Fellow", "Wifi down", "network", "high", 12)
        self.assertEqual(t["id"], "T001")
        events = s.history.for_ticket("T001")
        self.assertEqual([e["event_type"] for e in events], ["CREATE"])

    def test_duplicate_declined(self):
        s = quiet("n")
        s.create("Fellow", "Wifi down", "Network", "high", 5)
        self.assertIsNone(s.create("Fellow", "  WIFI  down ", "network", "low", 1))
        self.assertEqual(len(s.tickets), 1)
        self.assertEqual(s.history.count(), 1)

    def test_duplicate_accepted(self):
        s = quiet("y")
        s.create("Fellow", "Wifi down", "Network", "high", 5)
        self.assertIsNotNone(s.create("Fellow", "wifi down", "Network", "low", 1))
        self.assertEqual(len(s.tickets), 2)

    def test_full_lifecycle_events_in_order(self):
        s = quiet()
        s.create("Fellow", "Printer jam", "Hardware", "low", 1)
        s.assign("Fellow", "t001", "Ada")
        s.change_status("Ada", "T001", "in_progress")
        s.change_status("Ada", "T001", "resolved")
        s.reopen("Fellow", "T001")
        types = [e["event_type"] for e in s.history.for_ticket("T001")]
        self.assertEqual(types, ["CREATE", "ASSIGN", "START", "RESOLVE", "REOPEN"])

    def test_failed_operations_record_nothing(self):
        s = quiet()
        s.create("Fellow", "Printer jam", "Hardware", "low", 1)
        before = s.history.count()
        with self.assertRaises(ValueError):
            s.change_status("Ada", "T001", "in_progress")
        with self.assertRaises(ValueError):
            s.assign("Fellow", "T999", "Ada")
        with self.assertRaises(ValueError):
            s.reopen("Fellow", "T001")
        self.assertEqual(s.history.count(), before)

    def test_attention_queue_with_real_ticket_timestamps(self):
        s = quiet()
        t = s.create("Fellow", "Lab PC dead", "Hardware", "high", 1)
        t["created_at"] = (datetime.now() - timedelta(hours=10)).isoformat(timespec="seconds")
        queue = s.attention_queue()
        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0]["state"], "breached")

    def test_report_with_real_tickets(self):
        s = quiet()
        s.create("Fellow", "Lab PC dead", "Hardware", "high", 1)
        r = s.report()
        self.assertEqual(r["total"], 1)
        self.assertEqual(r["by_status"], {"open": 1})


if __name__ == "__main__":
    unittest.main()