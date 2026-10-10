import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from campusflow.workflow.storage import save_tickets, load_tickets


class TestTicketStorage(unittest.TestCase):

    def test_saved_tickets_can_be_loaded(self):
        tickets = [
            {
                "id": "T001",
                "title": "Wi-Fi not working",
                "status": "open",
                "priority": "high",
                "assigned_to": None,
            }
        ]

        with TemporaryDirectory() as directory:
            filename = Path(directory) / "tickets.json"

            save_tickets(tickets, filename)
            loaded_tickets = load_tickets(filename)

            self.assertEqual(loaded_tickets, tickets)


    def test_missing_file_returns_empty_list(self):

        with TemporaryDirectory() as directory:
            filename = Path(directory) / "missing.json"

            result = load_tickets(filename)

            self.assertEqual(result, [])


    def test_malformed_json_raises_value_error(self):

        with TemporaryDirectory() as directory:
            filename = Path(directory) / "tickets.json"

            filename.write_text(
                '{"id": "T001",',
                encoding="utf-8"
            )

            with self.assertRaises(ValueError):
                load_tickets(filename)
