import unittest
from datetime import datetime, timedelta, timezone

from campusflow_pro.reports import build_report

NOW = datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc)


def t(tid, priority, hours_old, status="open"):
    return {"id": tid, "priority": priority, "status": status,
            "created_at": NOW - timedelta(hours=hours_old)}


class TestReports(unittest.TestCase):

    def test_empty(self):
        r = build_report([], NOW)
        self.assertEqual(r["total"], 0)
        self.assertEqual(r["sla_breached"], 0)

    def test_counts_and_sla(self):
        tickets = [
            t(1, "critical", 5),                 # breached
            t(2, "critical", 3.5),               # at risk
            t(3, "low", 1),                      # ok
            t(4, "high", 50, "resolved"),        # resolved, ignored by SLA
        ]
        r = build_report(tickets, NOW)
        self.assertEqual(r["total"], 4)
        self.assertEqual(r["by_status"], {"open": 3, "resolved": 1})
        self.assertEqual(r["by_priority"]["critical"], 2)
        self.assertEqual(r["sla_breached"], 1)
        self.assertEqual(r["sla_at_risk"], 1)


if __name__ == "__main__":
    unittest.main()