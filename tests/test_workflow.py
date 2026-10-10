import unittest

from campusflow.workflow.assign_ticket import assign_ticket
from campusflow.workflow.ticket_status import (
    update_ticket_status, reopen_ticket)


class TestAssignTicket(unittest.TestCase):

    def test_assign_ticket_successfully(self):
        tickets = [
            {
                "id": "T001",
                "status": "open",
                "assigned_to": None
            }
        ]

        result = assign_ticket(tickets, "T001", "Daniel")

        self.assertEqual(result["assigned_to"], "Daniel")
        self.assertEqual(tickets[0]["assigned_to"], "Daniel")

    def test_empty_staff_name_is_rejected(self):
        tickets = [
            {
                "id": "T001",
                "status": "open",
                "assigned_to": None
            }
        ]

        with self.assertRaises(ValueError):
            assign_ticket(tickets, "T001", "")

        self.assertIsNone(tickets[0]["assigned_to"])

    def test_assign_resolved_ticket_is_rejected(self):
        tickets = [
            {
                "id": "T002",
                "status": "resolved",
                "assigned_to": None
            }
        ]

        with self.assertRaises(ValueError):
            assign_ticket(tickets, "T002", "Daniel")

        self.assertIsNone(tickets[0]["assigned_to"])

    def test_unknown_ticket_is_rejected(self):
        tickets = [
            {
                "id": "T001",
                "status": "open",
                "assigned_to": None
            }
        ]

        with self.assertRaises(ValueError):
            assign_ticket(tickets, "T999", "Daniel")

        self.assertIsNone(tickets[0]["assigned_to"])



class TestTicketStatus(unittest.TestCase):

    def test_assigned_ticket_can_move_to_in_progress(self):

        tickets = [
            {
                "id": "T001",
                "status": "open",
                "assigned_to": "Daniel"
            }
        ]

        result = update_ticket_status(
            tickets, "T001", "in_progress"
        )

        self.assertEqual(result["status"], "in_progress")

    def test_unassigned_ticket_cannot_move_to_in_progress(self):

        tickets = [
            {
                "id": "T002",
                "status": "open",
                "assigned_to": None
            }
        ]

        with self.assertRaises(ValueError):
            update_ticket_status(
                tickets, "T002", "in_progress"
            )

        self.assertEqual(tickets[0]["status"], "open")

    def test_in_progress_ticket_can_be_resolved(self):

        tickets = [
            {
                "id": "T003",
                "status": "in_progress",
                "assigned_to": "Daniel"
            }
        ]

        result = update_ticket_status(
            tickets, "T003", "resolved"
        )

        self.assertEqual(result["status"], "resolved")

    def test_open_ticket_cannot_be_resolved_directly(self):

        tickets = [
            {
                "id": "T004",
                "status": "open",
                "assigned_to": "Daniel"
            }
        ]

        with self.assertRaises(ValueError):
            update_ticket_status(
                tickets, "T004", "resolved"
            )

        self.assertEqual(tickets[0]["status"], "open")

    def test_resolved_ticket_cannot_be_modified(self):

        tickets = [
            {
                "id": "T005",
                "status": "resolved",
                "assigned_to": "Daniel"
            }
        ]

        with self.assertRaises(ValueError):
            update_ticket_status(
                tickets, "T005", "open"
            )

        self.assertEqual(tickets[0]["status"], "resolved")

    def test_unknown_ticket_id_is_rejected(self):

        tickets = []

        with self.assertRaises(ValueError):
            update_ticket_status(
                tickets, "T999", "in_progress"
            )


    def test_invalid_status_is_rejected_without_modifying_ticket(self):
        tickets = [
            {
                "id": "T001",
                "status": "open",
                "assigned_to": "Alice",
            }
        ]

        with self.assertRaises(ValueError):
            update_ticket_status(tickets, "T001", "closed")

        self.assertEqual(tickets[0]["status"], "open")        


class TestReopenTicket(unittest.TestCase):

    def test_resolved_ticket_can_be_reopened(self):
        tickets = [
            {"id": "T001", "status": "resolved", "assigned_to": "Daniel"}
        ]

        result = reopen_ticket(tickets, "T001")

        self.assertEqual(result["status"], "open")
        self.assertEqual(result["assigned_to"], "Daniel")

    def test_open_ticket_cannot_be_reopened(self):
        tickets = [
            {"id": "T001", "status": "open", "assigned_to": "Daniel"}
        ]

        with self.assertRaises(ValueError):
            reopen_ticket(tickets, "T001")

        self.assertEqual(tickets[0]["status"], "open")

    def test_in_progress_ticket_cannot_be_reopened(self):
        tickets = [
            {"id": "T001", "status": "in_progress", "assigned_to": "Daniel"}
        ]

        with self.assertRaises(ValueError):
            reopen_ticket(tickets, "T001")

        self.assertEqual(tickets[0]["status"], "in_progress")

    def test_unknown_ticket_cannot_be_reopened(self):
        tickets = [
            {"id": "T001", "status": "resolved", "assigned_to": "Daniel"}
        ]

        with self.assertRaises(ValueError):
            reopen_ticket(tickets, "T999")

        self.assertEqual(tickets[0]["status"], "resolved")

    def test_only_requested_ticket_is_reopened(self):
        tickets = [
            {
                "id": "T001",
                "status": "resolved",
                "assigned_to": "Alice",
            },
            {
                "id": "T002",
                "status": "in_progress",
                "assigned_to": "Bob",
            },
        ]

        reopen_ticket(tickets, "T001")

        self.assertEqual(tickets[0]["status"], "open")
        self.assertEqual(tickets[1]["status"], "in_progress")


if __name__ == "__main__":
    unittest.main()