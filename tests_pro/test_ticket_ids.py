
import unittest

from campusflow_pro.persistence.ticket_ids import next_ticket_id


class TestTicketIDContinuity(unittest.TestCase):

    def test_empty_ticket_list_starts_at_t001(self):
        self.assertEqual(next_ticket_id([]), "T001")

    def test_single_ticket_generates_next_id(self):
        tickets = [{"id": "T001"}]

        self.assertEqual(next_ticket_id(tickets), "T002")

    def test_multiple_tickets_generate_next_id(self):
        tickets = [
            {"id": "T001"},
            {"id": "T002"},
            {"id": "T003"},
        ]

        self.assertEqual(next_ticket_id(tickets), "T004")

    def test_uses_highest_id_not_list_length(self):
        tickets = [
            {"id": "T001"},
            {"id": "T009"},
        ]

        self.assertEqual(next_ticket_id(tickets), "T010")

    def test_unsorted_tickets(self):
        tickets = [
            {"id": "T015"},
            {"id": "T003"},
            {"id": "T010"},
        ]

        self.assertEqual(next_ticket_id(tickets), "T016")

    def test_supports_ids_above_999(self):
        tickets = [{"id": "T999"}]

        self.assertEqual(next_ticket_id(tickets), "T1000")

    def test_duplicate_ids_are_rejected(self):
        tickets = [
            {"id": "T001"},
            {"id": "T001"},
        ]

        with self.assertRaises(ValueError):
            next_ticket_id(tickets)

    def test_invalid_id_is_rejected(self):
        tickets = [{"id": "ABC001"}]

        with self.assertRaises(ValueError):
            next_ticket_id(tickets)

    def test_missing_id_is_rejected(self):
        tickets = [{"title": "Network issue"}]

        with self.assertRaises(ValueError):
            next_ticket_id(tickets)

    def test_invalid_collection_is_rejected(self):
        with self.assertRaises(TypeError):
            next_ticket_id("T001")

    def test_does_not_modify_original_tickets(self):
        tickets = [{"id": "T005"}]

        next_ticket_id(tickets)

        self.assertEqual(tickets, [{"id": "T005"}])


if __name__ == "__main__":
    unittest.main()
