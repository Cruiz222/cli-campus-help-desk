import unittest

from campusflow.workflow.reports import generate_report


class TestGenerateReport(unittest.TestCase):

    def test_report_counts_total_tickets(self):
        tickets = [
            {"status": "open", "priority": "high"},
            {"status": "resolved", "priority": "low"},
        ]

        report = generate_report(tickets)

        self.assertEqual(report["total"], 2)

    def test_report_counts_tickets_by_status(self):
        tickets = [
            {"status": "open", "priority": "high"},
            {"status": "open", "priority": "critical"},
            {"status": "resolved", "priority": "medium"},
        ]

        report = generate_report(tickets)

        self.assertEqual(report["by_status"]["open"], 2)
        self.assertEqual(report["by_status"]["in_progress"], 0)
        self.assertEqual(report["by_status"]["resolved"], 1)

    def test_report_counts_tickets_by_priority(self):
        tickets = [
            {"status": "open", "priority": "high"},
            {"status": "resolved", "priority": "high"},
            {"status": "in_progress", "priority": "critical"},
        ]

        report = generate_report(tickets)

        self.assertEqual(report["by_priority"]["critical"], 1)
        self.assertEqual(report["by_priority"]["high"], 2)
        self.assertEqual(report["by_priority"]["medium"], 0)
        self.assertEqual(report["by_priority"]["low"], 0)

    def test_empty_tickets_generate_zero_report(self):
        report = generate_report([])

        self.assertEqual(report["total"], 0)
        self.assertEqual(
            report["by_status"],
            {
                "open": 0,
                "in_progress": 0,
                "resolved": 0,
            },
        )
        self.assertEqual(
            report["by_priority"],
            {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
            },
        )