
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from campusflow_pro.persistence.bootstrap import (
    bootstrap_state,
    empty_state,
)
from campusflow_pro.persistence.storage import (
    save_state,
)


class TestBootstrap(unittest.TestCase):

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

    def test_empty_state_has_schema_version_two(self):
        state = empty_state()

        self.assertEqual(state["schema_version"], 2)

    def test_empty_state_has_empty_collections(self):
        state = empty_state()

        self.assertEqual(state["tickets"], [])
        self.assertEqual(state["events"], [])

    def test_empty_state_returns_independent_lists(self):
        first = empty_state()
        second = empty_state()

        first["tickets"].append({"id": "T001"})
        first["events"].append({"event_id": "E001"})

        self.assertEqual(second["tickets"], [])
        self.assertEqual(second["events"], [])

    def test_missing_file_returns_empty_state(self):
        state = bootstrap_state(self.path)

        self.assertEqual(state, empty_state())

    def test_missing_file_is_not_created_during_startup(self):
        bootstrap_state(self.path)

        self.assertFalse(self.path.exists())

    def test_valid_file_is_loaded(self):
        save_state(self.document, self.path)

        loaded = bootstrap_state(self.path)

        self.assertEqual(loaded, self.document)

    def test_valid_file_is_not_modified_during_startup(self):
        save_state(self.document, self.path)
        original_bytes = self.path.read_bytes()

        bootstrap_state(self.path)

        self.assertEqual(
            self.path.read_bytes(),
            original_bytes,
        )

    def test_corrupt_json_is_rejected(self):
        self.path.write_text(
            "{corrupt json",
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            bootstrap_state(self.path)

    def test_corrupt_json_is_not_overwritten(self):
        original = "{corrupt json"

        self.path.write_text(
            original,
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            bootstrap_state(self.path)

        self.assertEqual(
            self.path.read_text(encoding="utf-8"),
            original,
        )

    def test_invalid_schema_is_rejected(self):
        invalid = {
            "schema_version": 1,
            "tickets": [],
            "events": [],
        }

        self.path.write_text(
            json.dumps(invalid),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            bootstrap_state(self.path)

    def test_invalid_schema_is_not_overwritten(self):
        invalid = {
            "schema_version": 1,
            "tickets": [],
            "events": [],
        }

        original = json.dumps(invalid)

        self.path.write_text(
            original,
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            bootstrap_state(self.path)

        self.assertEqual(
            self.path.read_text(encoding="utf-8"),
            original,
        )

    def test_duplicate_ticket_ids_are_rejected(self):
        invalid = deepcopy(self.document)
        invalid["tickets"].append(
            deepcopy(invalid["tickets"][0])
        )

        self.path.write_text(
            json.dumps(invalid),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            bootstrap_state(self.path)

    def test_missing_parent_directory_is_rejected(self):
        path = (
            Path(self.directory.name)
            / "missing"
            / "state.json"
        )

        with self.assertRaises(FileNotFoundError):
            bootstrap_state(path)

    def test_directory_as_state_file_is_rejected(self):
        with self.assertRaises(IsADirectoryError):
            bootstrap_state(self.directory.name)

    def test_permission_error_is_not_hidden(self):
        with patch(
            "campusflow_pro.persistence.bootstrap.load_state",
            side_effect=PermissionError("Access denied"),
        ):
            with self.assertRaises(PermissionError):
                bootstrap_state(self.path)

    def test_loaded_state_can_be_saved_again(self):
        save_state(self.document, self.path)

        loaded = bootstrap_state(self.path)
        loaded["tickets"][0]["title"] = "Updated outage"

        save_state(loaded, self.path)

        reloaded = bootstrap_state(self.path)

        self.assertEqual(
            reloaded["tickets"][0]["title"],
            "Updated outage",
        )


if __name__ == "__main__":
    unittest.main()
