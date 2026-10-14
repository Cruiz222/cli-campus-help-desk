
import unittest
from datetime import datetime, timedelta, timezone

from campusflow_pro.sla.policy import calculate_due_at


class TestSLAPolicy(unittest.TestCase):

    def setUp(self):
        self.cycle_start = datetime(
            2026, 10, 14, 10, 0,
            tzinfo=timezone.utc
        )

    def test_critical_ticket_due_after_60_minutes(self):
        expected = self.cycle_start + timedelta(minutes=60)

        result = calculate_due_at("critical", self.cycle_start)

        self.assertEqual(result, expected)

    def test_high_ticket_due_after_240_minutes(self):
        expected = self.cycle_start + timedelta(minutes=240)

        result = calculate_due_at("high", self.cycle_start)

        self.assertEqual(result, expected)

    def test_medium_ticket_due_after_1440_minutes(self):
        expected = self.cycle_start + timedelta(minutes=1440)

        result = calculate_due_at("medium", self.cycle_start)

        self.assertEqual(result, expected)

    def test_low_ticket_due_after_2880_minutes(self):
        expected = self.cycle_start + timedelta(minutes=2880)

        result = calculate_due_at("low", self.cycle_start)

        self.assertEqual(result, expected)

    def test_unsupported_priority_raises_value_error(self):
        with self.assertRaises(ValueError):
            calculate_due_at("urgent", self.cycle_start)

    def test_naive_datetime_raises_value_error(self):
        naive_time = datetime(2026, 10, 14, 10, 0)

        with self.assertRaises(ValueError):
            calculate_due_at("critical", naive_time)

    def test_non_datetime_input_raises_type_error(self):
        with self.assertRaises(TypeError):
            calculate_due_at(
                "critical",
                "2026-10-14T10:00:00+00:00"
            )

    def test_result_is_timezone_aware(self):
        result = calculate_due_at(
            "critical",
            self.cycle_start
        )

        self.assertIsNotNone(result.tzinfo)
        self.assertEqual(result.utcoffset(), timedelta(0))

    def test_non_utc_timezone_is_normalized_to_utc(self):
        west_africa_time = timezone(timedelta(hours=1))

        cycle_start = datetime(
            2026, 10, 14, 11, 0,
            tzinfo=west_africa_time
        )

        expected = datetime(
            2026, 10, 14, 11, 0,
            tzinfo=timezone.utc
        )

        result = calculate_due_at("critical", cycle_start)

        self.assertEqual(result, expected)
        self.assertEqual(result.tzinfo, timezone.utc)

    def test_calculation_does_not_modify_start_time(self):
        original = self.cycle_start

        calculate_due_at("critical", self.cycle_start)

        self.assertEqual(self.cycle_start, original)


if __name__ == "__main__":
    unittest.main()
