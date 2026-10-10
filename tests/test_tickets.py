import unittest
from campusflow import tickets 
from campusflow.tickets import (
    VALID_CATEGORIES,
    VALID_URGENCIES
)


class TestValidateTitle(unittest.TestCase):
    #TESTS FOR validate_title
    def test_validate_title(self):
        result = tickets.validate_title("   Wi-Fi is down   ")
        self.assertEqual(result, "Wi-Fi is down")

    def test_blank_title(self):
        with self.assertRaises(ValueError):
            tickets.validate_title("  ")

    #TESTS FOR validate_category
    def test_validate_category(self):
        result = tickets.validate_category(VALID_CATEGORIES, "  NetWork   ")
        self.assertEqual(result, "Network")

    def test_blank_category(self):
        with self.assertRaises(ValueError):
            tickets.validate_category(VALID_CATEGORIES, "    ")
    
    def test_category_variants_normalized(self):
        variant_categories = ["hArdWare", "SOFTWARE", "other"]
        for each_category in variant_categories:
            result = tickets.validate_category(VALID_CATEGORIES, each_category)
            self.assertIn(result, VALID_CATEGORIES)

    def test_trimmed_category_spaces(self):
        result = tickets.validate_category(VALID_CATEGORIES, "  other  ")
        self.assertEqual(result, "Other")

    def test_invalid_category_rejected(self):
        with self.assertRaises(ValueError):
            tickets.validate_category(VALID_CATEGORIES, "Printer")

    def test_blank_category_rejected(self):
        with self.assertRaises(ValueError):
            tickets.validate_category(VALID_CATEGORIES, "")
    
    def test_non_text_category_rejected(self):
        with self.assertRaises(ValueError):
            tickets.validate_category(VALID_CATEGORIES, None)

    #TESTS FOR validate_urgency
    def test_validate_urgency(self):
        result = tickets.validate_urgency(VALID_URGENCIES, "low")
        self.assertEqual(result, "low")

    def test_urgency_variants_normalized(self):
        variant_urgencies = ["hIGH", "MEDIUM", "lOw"]
        for each_urgency in variant_urgencies:
            result = tickets.validate_urgency(VALID_URGENCIES, each_urgency)
            self.assertIn(result, VALID_URGENCIES)

    def test_trimmed_urgency_spaces(self):
        result = tickets.validate_urgency(VALID_URGENCIES, "  low  ")
        self.assertEqual(result, "low")

    def test_invalid_urgency_rejected(self):
        with self.assertRaises(ValueError):
            tickets.validate_urgency(VALID_URGENCIES, "urgent")

    def test_blank_urgency_rejected(self):
        with self.assertRaises(ValueError):
            tickets.validate_urgency(VALID_URGENCIES, "")

    def test_non_text_urgency_rejected(self):
        with self.assertRaises(ValueError):
            tickets.validate_urgency(VALID_URGENCIES, None)

    def test_validate_affected_users(self):
        result = tickets.validate_affected_users('5')
        self.assertEqual(result, 5)


    #TESTS FOR affected_users
    def test_affected_users_boundary(self):
            result = tickets.validate_affected_users(1)
            self.assertEqual(result, 1)

    def test_affected_users_zero_rejected(self):
         with self.assertRaises(ValueError):
            tickets.validate_affected_users('0')

    def test_affected_users_negative_rejected(self):
        with self.assertRaises(ValueError):
            tickets.validate_affected_users('-3')

    def test_affected_users_decimal_rejected(self):
        with self.assertRaises(ValueError):
            tickets.validate_affected_users(2.5)

    def test_affected_users_text__rejected(self):
        with self.assertRaises(ValueError):
            tickets.validate_affected_users('five')

    def test_affected_users_boolean__rejected(self):
        with self.assertRaises(ValueError):
            tickets.validate_affected_users(True)

    #TESTS FOR calculate_priority
    # --- Roadmap Required Scenarios ---

    def test_high_urgency_12_users_returns_critical(self):
        self.assertEqual(tickets.calculate_priority("high", 12), "critical")

    def test_high_urgency_2_users_returns_high(self):
        self.assertEqual(tickets.calculate_priority("high", 2), "high")

    def test_low_urgency_4_users_returns_medium(self):
        self.assertEqual(tickets.calculate_priority("low", 4), "medium")

    def test_low_urgency_1_user_returns_low(self):
        self.assertEqual(tickets.calculate_priority("low", 1), "low")

    # --- Boundary & Edge-case Tests ---

    def test_high_urgency_exactly_10_users_returns_critical(self):
        self.assertEqual(tickets.calculate_priority("high", 10), "critical")

    def test_high_urgency_9_users_returns_high(self):
        self.assertEqual(tickets.calculate_priority("high", 9), "high")

    def test_low_urgency_exactly_10_users_returns_high(self):
        self.assertEqual(tickets.calculate_priority("low", 10), "high")

    def test_low_urgency_9_users_returns_medium(self):
        self.assertEqual(tickets.calculate_priority("low", 9), "medium")

    def test_low_urgency_exactly_3_users_returns_medium(self):
        self.assertEqual(tickets.calculate_priority("low", 3), "medium")

    def test_low_urgency_2_users_returns_low(self):
        self.assertEqual(tickets.calculate_priority("low", 2), "low")

    def test_medium_urgency_1_user_returns_medium(self):
        self.assertEqual(tickets.calculate_priority("medium", 1), "medium")

    def test_medium_urgency_10_users_returns_high(self):
        self.assertEqual(tickets.calculate_priority("medium", 10), "high")

    #TESTS FOR generate_ticket_id
    def test_empty_list_returns_t001(self):
        ticket_list = []
        result = tickets.generate_ticket_id(ticket_list)
        self.assertEqual(result, "T001")

    def test_single_ticket_returns_t002(self):
        ticket_list = [{"id": "T001"}]
        result = tickets.generate_ticket_id(ticket_list)
        self.assertEqual(result, "T002")

    def test_sequential_tickets_returns_t003(self):
        ticket_list = [{"id": "T001"}, {"id": "T002"}]
        result = tickets.generate_ticket_id(ticket_list)
        self.assertEqual(result, "T003")

    def test_gap_in_numbering_uses_max_id(self):
        ticket_list = [{"id": "T001"}, {"id": "T005"}]
        result = tickets.generate_ticket_id(ticket_list)
        self.assertEqual(result, "T006")

    def test_numeric_ordering_over_text_ordering(self):
        ticket_list = [{"id": "T009"}, {"id": "T010"}]
        result = tickets.generate_ticket_id(ticket_list)
        self.assertEqual(result, "T011")

    def test_unordered_list_returns_correct_next_id(self):
        ticket_list = [{"id": "T003"}, {"id": "T001"}, {"id": "T002"}]
        result = tickets.generate_ticket_id(ticket_list)
        self.assertEqual(result, "T004")

    def test_generate_ticket_id_does_not_modify_list(self):
        ticket_list = [{"id": "T001"}, {"id": "T002"}]
        initial_length = len(ticket_list)
        tickets.generate_ticket_id(ticket_list)
        self.assertEqual(len(ticket_list), initial_length)
if __name__ == "__main__":
    unittest.main()
