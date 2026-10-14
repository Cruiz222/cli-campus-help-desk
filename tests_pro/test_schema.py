
import unittest
from copy import deepcopy

from campusflow_pro.persistence.schema import (
    validate_document,
)


class TestSchemaValidation(unittest.TestCase):

    def setUp(self):
        self.ticket = {
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

        self.document = {
            "schema_version": 2,
            "tickets": [self.ticket],
            "events": [],
        }

    def make_event(
        self,
        event_id="E001",
        event_type="CREATE",
        ticket_id="T001",
        cycle=0,
    ):
        event = {
            "event_id": event_id,
            "ticket_id": ticket_id,
            "event_type": event_type,
            "actor": "staff",
            "timestamp": "2026-10-14T12:00:00+00:00",
            "before_status": None,
            "after_status": "open",
            "details": {},
        }

        if event_type == "ESCALATE":
            event["actor"] = "system"
            event["before_status"] = "open"
            event["after_status"] = "open"
            event["details"] = {
                "escalation_cycle": cycle,
            }

        return event

    def test_valid_document_passes(self):
        self.assertIs(
            validate_document(self.document),
            self.document,
        )

    def test_empty_document_passes(self):
        document = {
            "schema_version": 2,
            "tickets": [],
            "events": [],
        }

        validate_document(document)

    def test_invalid_schema_version_rejected(self):
        self.document["schema_version"] = 1

        with self.assertRaises(ValueError):
            validate_document(self.document)

    def test_boolean_schema_version_rejected(self):
        self.document["schema_version"] = True

        with self.assertRaises(ValueError):
            validate_document(self.document)

    def test_missing_tickets_rejected(self):
        del self.document["tickets"]

        with self.assertRaises(ValueError):
            validate_document(self.document)

    def test_duplicate_ticket_ids_rejected(self):
        self.document["tickets"].append(
            deepcopy(self.ticket)
        )

        with self.assertRaises(ValueError):
            validate_document(self.document)

    def test_missing_ticket_field_rejected(self):
        del self.ticket["due_at"]

        with self.assertRaises(ValueError):
            validate_document(self.document)

    def test_naive_timestamp_rejected(self):
        self.ticket["created_at"] = (
            "2026-10-14T10:00:00"
        )

        with self.assertRaises(ValueError):
            validate_document(self.document)

    def test_invalid_priority_rejected(self):
        self.ticket["priority"] = "urgent"

        with self.assertRaises(ValueError):
            validate_document(self.document)

    def test_invalid_cycle_rejected(self):
        self.ticket["escalation_cycle"] = -1

        with self.assertRaises(ValueError):
            validate_document(self.document)

    def test_boolean_cycle_rejected(self):
        self.ticket["escalation_cycle"] = True

        with self.assertRaises(ValueError):
            validate_document(self.document)

    def test_marker_greater_than_cycle_rejected(self):
        self.ticket["escalated_cycle"] = 2

        with self.assertRaises(ValueError):
            validate_document(self.document)

    def test_resolved_ticket_requires_resolved_at(self):
        self.ticket["status"] = "resolved"

        with self.assertRaises(ValueError):
            validate_document(self.document)

    def test_valid_audit_event_passes(self):
        self.document["events"].append(
            self.make_event()
        )

        validate_document(self.document)

    def test_duplicate_event_ids_rejected(self):
        event = self.make_event()

        self.document["events"] = [
            event,
            deepcopy(event),
        ]

        with self.assertRaises(ValueError):
            validate_document(self.document)

    def test_event_with_unknown_ticket_rejected(self):
        self.document["events"].append(
            self.make_event(ticket_id="T999")
        )

        with self.assertRaises(ValueError):
            validate_document(self.document)

    def test_duplicate_escalation_cycle_rejected(self):
        first = self.make_event(
            event_id="E001",
            event_type="ESCALATE",
        )

        second = self.make_event(
            event_id="E002",
            event_type="ESCALATE",
        )

        self.document["events"] = [
            first,
            second,
        ]

        with self.assertRaises(ValueError):
            validate_document(self.document)

    def test_validation_does_not_mutate_document(self):
        original = deepcopy(self.document)

        validate_document(self.document)

        self.assertEqual(
            self.document,
            original,
        )

    # New regression tests.

    def test_inconsistent_priority_is_rejected(self):
        self.ticket["priority"] = "low"

        with self.assertRaises(ValueError):
            validate_document(self.document)

    def test_escalated_marker_without_event_is_rejected(self):
        self.ticket["escalated_cycle"] = 0

        with self.assertRaises(ValueError):
            validate_document(self.document)

    def test_escalation_event_without_marker_is_rejected(self):
        self.document["events"].append(
            self.make_event(
                event_type="ESCALATE",
                cycle=0,
            )
        )

        with self.assertRaises(ValueError):
            validate_document(self.document)

    def test_future_cycle_event_is_rejected(self):
        self.document["events"].append(
            self.make_event(
                event_type="ESCALATE",
                cycle=1,
            )
        )

        with self.assertRaises(ValueError):
            validate_document(self.document)

    # Additional successful integration scenarios.

    def test_matching_escalation_marker_and_event_pass(self):
        self.ticket["escalated_cycle"] = 0
        self.ticket["updated_at"] = (
            "2026-10-14T12:00:00+00:00"
        )

        self.document["events"].append(
            self.make_event(
                event_type="ESCALATE",
                cycle=0,
            )
        )

        validate_document(self.document)

    def test_historical_escalation_event_is_preserved(self):
        self.ticket["escalation_cycle"] = 1
        self.ticket["escalated_cycle"] = None

        self.ticket["updated_at"] = (
            "2026-10-14T12:00:00+00:00"
        )

        self.ticket["due_at"] = (
            "2026-10-14T13:00:00+00:00"
        )

        self.document["events"].append(
            self.make_event(
                event_type="ESCALATE",
                cycle=0,
            )
        )

        validate_document(self.document)

    def test_previous_cycle_marker_is_rejected(self):
        self.ticket["escalation_cycle"] = 2
        self.ticket["escalated_cycle"] = 1

        with self.assertRaises(ValueError):
            validate_document(self.document)


if __name__ == "__main__":
    unittest.main()
