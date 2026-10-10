import unittest

from campusflow.workflow.work_queue import get_work_queue


class TestWorkQueue(unittest.TestCase):

    def test_tickets_are_sorted_by_priority(self):
        tickets = [
            {"id": "T001", "priority": "low", "status": "open"},
            {"id": "T002", "priority": "critical", "status": "open"},
            {"id": "T003", "priority": "medium", "status": "open"},
            {"id": "T004", "priority": "high", "status": "open"},
        ]

        result = get_work_queue(tickets)

        self.assertEqual(
            [ticket["id"] for ticket in result],
            ["T002", "T004", "T003", "T001"]
        )

    def test_tickets_with_same_priority_are_sorted_by_numeric_id(self):
        tickets = [
            {"id": "T010", "priority": "high", "status": "open"},
            {"id": "T002", "priority": "high", "status": "open"},
            {"id": "T001", "priority": "high", "status": "open"},
        ]

        result = get_work_queue(tickets)

        self.assertEqual(
            [ticket["id"] for ticket in result],
            ["T001", "T002", "T010"]
        )

    def test_non_open_tickets_are_excluded(self):
        tickets = [
            {"id": "T001", "priority": "critical", "status": "resolved"},
            {"id": "T002", "priority": "high", "status": "in_progress"},
            {"id": "T003", "priority": "low", "status": "open"},
        ]

        result = get_work_queue(tickets)

        self.assertEqual(
            [ticket["id"] for ticket in result],
            ["T003"]
        )

    def test_empty_queue_returns_empty_list(self):
        self.assertEqual(get_work_queue([]), [])

    def test_original_ticket_order_is_unchanged(self):
        tickets = [
            {"id": "T010", "priority": "low", "status": "open"},
            {"id": "T001", "priority": "critical", "status": "open"},
        ]

        get_work_queue(tickets)

        self.assertEqual(
            [ticket["id"] for ticket in tickets],
            ["T010", "T001"]
        )