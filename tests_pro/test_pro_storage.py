
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from campusflow_pro.persistence.storage import (
    load_state,
    save_state,
)


class TestProStorage(unittest.TestCase):

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)

        self.path = Path(self.directory.name) / "state.json"

        self.document = {
            "schema_version": 2,
            "tickets": [
                {
                    "id": "T001",
                    "title": "Network outage",
                    "category": "Network",
                    "urgency": "high",
                    "affected_users": 20,
                    "priority": "critical",
                    "status": "open",
                    "assigned_to": None,
                    "created_at": "2026-10-14T10:00:00+00:00",
                    "updated_at": "2026-10-14T10:00:00+00:00",
                    "started_at": None,
                    "resolved_at": None,
                    "due_at": "2026-10-14T11:00:00+00:00",
                    "escalation_cycle": 0,
                    "escalated_cycle": None,
                }
            ],
            "events": [],
        }

    def test_save_creates_json_file(self):
        save_state(self.document, self.path)

        self.assertTrue(self.path.exists())

    def test_saved_file_contains_schema_version(self):
        save_state(self.document, self.path)

        with self.path.open(encoding="utf-8") as file:
            saved = json.load(file)

        self.assertEqual(saved["schema_version"], 2)

    def test_round_trip_preserves_document(self):
        save_state(self.document, self.path)

        loaded = load_state(self.path)

        self.assertEqual(loaded, self.document)

    def test_save_does_not_mutate_document(self):
        original = deepcopy(self.document)

        save_state(self.document, self.path)

        self.assertEqual(self.document, original)

    def test_save_rejects_invalid_document(self):
        self.document["schema_version"] = 1

        with self.assertRaises(ValueError):
            save_state(self.document, self.path)

        self.assertFalse(self.path.exists())

    def test_invalid_save_preserves_existing_file(self):
        save_state(self.document, self.path)
        original_bytes = self.path.read_bytes()

        invalid = deepcopy(self.document)
        invalid["tickets"][0]["due_at"] = "invalid"

        with self.assertRaises(ValueError):
            save_state(invalid, self.path)

        self.assertEqual(self.path.read_bytes(), original_bytes)

    def test_missing_file_raises_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            load_state(self.path)

    def test_corrupt_json_is_rejected(self):
        self.path.write_text("{invalid json", encoding="utf-8")

        with self.assertRaises(ValueError):
            load_state(self.path)

    def test_invalid_schema_is_rejected_on_load(self):
        self.path.write_text(
            json.dumps({
                "schema_version": 1,
                "tickets": [],
                "events": [],
            }),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            load_state(self.path)

    def test_atomic_replace_failure_preserves_existing_file(self):
        save_state(self.document, self.path)
        original_bytes = self.path.read_bytes()

        updated = deepcopy(self.document)
        updated["tickets"][0]["title"] = "Updated outage"

        with patch(
            "campusflow_pro.persistence.storage.os.replace",
            side_effect=OSError("Simulated replacement failure"),
        ):
            with self.assertRaises(OSError):
                save_state(updated, self.path)

        self.assertEqual(self.path.read_bytes(), original_bytes)

    def test_failed_replace_cleans_up_temporary_file(self):
        with patch(
            "campusflow_pro.persistence.storage.os.replace",
            side_effect=OSError("Simulated replacement failure"),
        ):
            with self.assertRaises(OSError):
                save_state(self.document, self.path)

        self.assertEqual(list(self.path.parent.iterdir()), [])

    def test_successful_save_leaves_no_temporary_files(self):
        save_state(self.document, self.path)

        files = list(self.path.parent.iterdir())

        self.assertEqual(files, [self.path])

    def test_missing_destination_directory_is_rejected(self):
        invalid_path = (
            Path(self.directory.name)
            / "missing"
            / "state.json"
        )

        with self.assertRaises(FileNotFoundError):
            save_state(self.document, invalid_path)

    def test_save_replaces_existing_state(self):
        save_state(self.document, self.path)

        updated = deepcopy(self.document)
        updated["tickets"][0]["title"] = "Updated network outage"

        save_state(updated, self.path)

        self.assertEqual(
            load_state(self.path)["tickets"][0]["title"],
            "Updated network outage",
        )

    def test_tickets_and_events_are_saved_together(self):
        self.document["events"].append({
            "event_id": "E001",
            "ticket_id": "T001",
            "event_type": "CREATE",
            "actor": "staff",
            "timestamp": "2026-10-14T10:00:00+00:00",
            "before_status": None,
            "after_status": "open",
            "details": {},
        })

        save_state(self.document, self.path)
        loaded = load_state(self.path)

        self.assertEqual(len(loaded["tickets"]), 1)
        self.assertEqual(len(loaded["events"]), 1)
        self.assertEqual(
            loaded["events"][0]["event_type"],
            "CREATE",
        )


if __name__ == "__main__":
    unittest.main()
