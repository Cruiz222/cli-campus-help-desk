
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from campusflow_pro.application import ProApplication
from main_pro import run_cli


class TestMainPro(unittest.TestCase):

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)

        self.path = Path(self.directory.name) / "state.json"
        self.output = []

        self.app = ProApplication(
            self.path,
            clock=lambda: datetime(
                2026, 10, 14, 10, 0,
                tzinfo=timezone.utc,
            ),
            input_fn=lambda prompt: "yes",
            output_fn=self.output.append,
        )

    def run_commands(self, commands):
        iterator = iter(commands)

        run_cli(
            self.app,
            input_fn=lambda prompt: next(iterator),
            output_fn=self.output.append,
        )

    def test_exit(self):
        self.run_commands(["13"])

        self.assertIn("\nGoodbye!", self.output)

    def test_create_ticket(self):
        self.run_commands([
            "1",
            "admin",
            "Network outage",
            "Network",
            "high",
            "20",
            "13",
        ])

        self.assertEqual(len(self.app.tickets()), 1)
        self.assertEqual(len(self.app.events()), 1)

    def test_create_and_view_tickets(self):
        self.run_commands([
            "1",
            "admin",
            "Broken keyboard",
            "Hardware",
            "low",
            "1",
            "2",
            "13",
        ])

        self.assertTrue(
            any("Broken keyboard" in line for line in self.output)
        )

    def test_assign_ticket(self):
        ticket = self.app.create(
            "admin",
            "Broken keyboard",
            "Hardware",
            "low",
            1,
        )

        self.run_commands([
            "3",
            "admin",
            ticket["id"],
            "Alice",
            "13",
        ])

        self.assertEqual(
            self.app.tickets()[0]["assigned_to"],
            "Alice",
        )

    def test_start_and_resolve_ticket(self):
        ticket = self.app.create(
            "admin",
            "Network outage",
            "Network",
            "high",
            20,
        )

        self.app.assign(
            "admin",
            ticket["id"],
            "Alice",
        )

        self.run_commands([
            "4", "Alice", ticket["id"],
            "5", "Alice", ticket["id"],
            "13",
        ])

        self.assertEqual(
            self.app.tickets()[0]["status"],
            "resolved",
        )

    def test_invalid_option(self):
        self.run_commands(["invalid", "13"])

        self.assertIn("\nInvalid option.", self.output)

    def test_invalid_ticket_does_not_crash_cli(self):
        self.run_commands([
            "3",
            "admin",
            "T999",
            "Alice",
            "13",
        ])

        self.assertTrue(
            any("Error:" in line for line in self.output)
        )

    def test_history_display(self):
        ticket = self.app.create(
            "admin",
            "Network outage",
            "Network",
            "high",
            20,
        )

        self.run_commands([
            "7",
            ticket["id"],
            "13",
        ])

        self.assertTrue(
            any("CREATE" in line for line in self.output)
        )

    def test_report_display(self):
        self.run_commands(["10", "13"])

        self.assertTrue(
            any("CAMPUSFLOW PRO REPORT" in line for line in self.output)
        )


if __name__ == "__main__":
    unittest.main()
