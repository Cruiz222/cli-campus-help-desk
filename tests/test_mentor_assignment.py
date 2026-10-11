import unittest

from campusflow.workflow.mentor_assignment import (
    MENTORS,
    assign_mentor_automatically,
    get_mentor_queue,
    start_mentor_ticket,
    resolve_mentor_ticket,
)


def make_ticket(number, status="open", mentor=None):
    return {
        "id": f"T{number:03d}",
        "title": f"Test issue {number}",
        "category": "Network",
        "urgency": "high",
        "affected_users": 2,
        "priority": "high",
        "status": status,
        "assigned_to": mentor,
        "issuer": f"FELLOW{number:03d}",
    }


class TestAutomaticMentorAssignment(unittest.TestCase):

    def test_six_tickets_are_distributed_evenly(self):
        tickets = []

        for number in range(1, 7):
            ticket = make_ticket(number)
            tickets.append(ticket)
            assign_mentor_automatically(tickets, ticket)

        assignments = [
            ticket["assigned_to"] for ticket in tickets
        ]

        self.assertEqual(assignments, list(MENTORS))

    def test_new_ticket_goes_to_least_busy_mentor(self):
        tickets = [
            make_ticket(1, mentor=MENTORS[0]),
            make_ticket(2, mentor=MENTORS[0]),
        ]

        new_ticket = make_ticket(3)
        tickets.append(new_ticket)

        mentor = assign_mentor_automatically(
            tickets, new_ticket
        )

        self.assertEqual(mentor, MENTORS[1])

    def test_resolved_tickets_do_not_count_as_pending_work(self):
        tickets = [
            make_ticket(1, "resolved", MENTORS[0]),
            make_ticket(2, "open", MENTORS[1]),
        ]

        new_ticket = make_ticket(3)
        tickets.append(new_ticket)

        mentor = assign_mentor_automatically(
            tickets, new_ticket
        )

        self.assertEqual(mentor, MENTORS[0])

    def test_mentor_cannot_start_two_tickets(self):
        tickets = [
            make_ticket(1, "in_progress", MENTORS[0]),
            make_ticket(2, "open", MENTORS[0]),
        ]

        with self.assertRaises(ValueError):
            start_mentor_ticket(tickets, "T002", MENTORS[0])

        self.assertEqual(tickets[1]["status"], "open")

    def test_mentor_cannot_start_another_mentors_ticket(self):
        tickets = [
            make_ticket(1, "open", MENTORS[0]),
        ]

        with self.assertRaises(ValueError):
            start_mentor_ticket(tickets, "T001", MENTORS[1])

    def test_mentor_can_start_and_resolve_ticket(self):
        tickets = [
            make_ticket(1, "open", MENTORS[0]),
        ]

        start_mentor_ticket(tickets, "T001", MENTORS[0])
        self.assertEqual(tickets[0]["status"], "in_progress")

        resolve_mentor_ticket(tickets, "T001", MENTORS[0])
        self.assertEqual(tickets[0]["status"], "resolved")

    def test_queue_contains_only_mentors_open_tickets(self):
        tickets = [
            make_ticket(1, "open", MENTORS[0]),
            make_ticket(2, "in_progress", MENTORS[0]),
            make_ticket(3, "open", MENTORS[1]),
        ]

        queue = get_mentor_queue(tickets, MENTORS[0])

        self.assertEqual(
            [ticket["id"] for ticket in queue],
            ["T001"],
        )


if __name__ == "__main__":
    unittest.main()