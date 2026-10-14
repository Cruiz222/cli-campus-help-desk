import unittest
from datetime import datetime, timedelta, timezone

from campusflow_pro.sla.attention_queue import attention_queue, sla_status

NOW = datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc)


def ticket(tid, priority, hours_old, status="open"):
    return {"id": tid, "priority": priority, "status": status,
            "created_at": NOW - timedelta(hours=hours_old)}


class TestAttentionQueue(unittest.TestCase):

    def test_breached(self):
        self.assertEqual(sla_status(ticket(1, "critical", 5), NOW)["state"], "breached")

    def test_at_risk(self):
        self.assertEqual(sla_status(ticket(1, "critical", 3.5), NOW)["state"], "at_risk")

    def test_ok(self):
        self.assertEqual(sla_status(ticket(1, "critical", 1), NOW)["state"], "ok")

    def test_resolved_excluded(self):
        q = attention_queue([ticket(1, "critical", 10, "resolved")], NOW)
        self.assertEqual(q, [])

    def test_ok_tickets_excluded(self):
        self.assertEqual(attention_queue([ticket(1, "low", 1)], NOW), [])

    def test_ordering(self):
        tickets = [
            ticket(1, "critical", 3.5),   # at risk
            ticket(2, "low", 100),        # breached, low
            ticket(3, "high", 20),        # breached, high
        ]
        ids = [i["ticket"]["id"] for i in attention_queue(tickets, NOW)]
        self.assertEqual(ids, [3, 2, 1])

    def test_unknown_priority_rejected(self):
        with self.assertRaises(ValueError):
            sla_status(ticket(1, "urgent", 1), NOW)

    # def test_naive_timestamp_rejected(self):
    #     t = {"id": 1, "priority": "low", "status": "open",
    #          "created_at": datetime(2026, 10, 14)}
    #     with self.assertRaises(ValueError):
    #         sla_status(t, NOW)

    def test_naive_created_at_is_treated_as_local_time(self):
        created = datetime.now() - timedelta(hours=5)
        t = {"id": "T001", "priority": "critical", "status": "open",
             "created_at": created.isoformat(timespec="seconds")}
        info = sla_status(t, datetime.now(timezone.utc))
        self.assertEqual(info["state"], "breached")

    def test_naive_now_rejected(self):
        with self.assertRaises(ValueError):
            sla_status(ticket(1, "low", 1), datetime(2026, 10, 14))

if __name__ == "__main__":
    unittest.main()