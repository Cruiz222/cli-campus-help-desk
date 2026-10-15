
import unittest
from datetime import datetime, timedelta, timezone

from campusflow_pro.sla.attention_queue import (
    attention_queue,
    sla_status,
)
from campusflow_pro.sla.policy import calculate_due_at


NOW = datetime(
    2026, 10, 14, 12, 0, tzinfo=timezone.utc
)


def pro_ticket(
    ticket_id,
    priority,
    created_at,
    due_at,
    status="open",
):
    return {
        "id": ticket_id,
        "priority": priority,
        "status": status,
        "created_at": created_at.isoformat(),
        "due_at": due_at.isoformat(),
    }


class TestAttentionQueueIntegration(unittest.TestCase):

    def test_critical_uses_one_hour_deadline(self):
        created = NOW - timedelta(hours=2)
        due = calculate_due_at("critical", created)

        ticket = pro_ticket(
            "T001", "critical", created, due
        )

        info = sla_status(ticket, NOW)

        self.assertEqual(info["deadline"], due)
        self.assertEqual(info["state"], "breached")

    def test_high_uses_four_hour_deadline(self):
        created = NOW - timedelta(hours=5)
        due = calculate_due_at("high", created)

        ticket = pro_ticket(
            "T002", "high", created, due
        )

        self.assertEqual(
            sla_status(ticket, NOW)["state"],
            "breached",
        )

    def test_low_uses_forty_eight_hour_deadline(self):
        created = NOW - timedelta(hours=50)
        due = calculate_due_at("low", created)

        ticket = pro_ticket(
            "T003", "low", created, due
        )

        self.assertEqual(
            sla_status(ticket, NOW)["state"],
            "breached",
        )

    def test_exact_deadline_is_not_overdue(self):
        created = NOW - timedelta(hours=1)
        due = calculate_due_at("critical", created)

        ticket = pro_ticket(
            "T004", "critical", created, due
        )

        self.assertEqual(
            sla_status(ticket, NOW)["state"],
            "at_risk",
        )

    def test_one_second_after_deadline_is_breached(self):
        due = NOW - timedelta(seconds=1)
        created = due - timedelta(hours=1)

        ticket = pro_ticket(
            "T005", "critical", created, due
        )

        self.assertEqual(
            sla_status(ticket, NOW)["state"],
            "breached",
        )

    def test_reopened_ticket_uses_new_deadline(self):
        original_created = NOW - timedelta(days=5)
        new_due = NOW + timedelta(hours=1)

        ticket = pro_ticket(
            "T006",
            "high",
            original_created,
            new_due,
        )

        info = sla_status(ticket, NOW)

        self.assertEqual(
            info["deadline"],
            new_due,
        )
        self.assertEqual(
            info["state"],
            "at_risk",
        )

    def test_resolved_ticket_excluded(self):
        created = NOW - timedelta(hours=5)
        due = calculate_due_at("critical", created)

        ticket = pro_ticket(
            "T007",
            "critical",
            created,
            due,
            status="resolved",
        )

        self.assertEqual(
            attention_queue([ticket], NOW),
            [],
        )

    def test_breached_tickets_come_first(self):
        breached_created = NOW - timedelta(hours=2)
        breached_due = calculate_due_at(
            "critical", breached_created
        )

        at_risk_created = NOW - timedelta(hours=3, minutes=30)
        at_risk_due = calculate_due_at(
            "high", at_risk_created
        )

        tickets = [
            pro_ticket(
                "T008",
                "high",
                at_risk_created,
                at_risk_due,
            ),
            pro_ticket(
                "T009",
                "critical",
                breached_created,
                breached_due,
            ),
        ]

        result = attention_queue(tickets, NOW)

        self.assertEqual(
            [item["ticket"]["id"] for item in result],
            ["T009", "T008"],
        )


if __name__ == "__main__":
    unittest.main()
