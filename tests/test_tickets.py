import unittest

from campusflow import tickets 

from campusflow.tickets import (

    VALID_CATEGORIES,

    VALID_URGENCIES

)





class TestValidateTitle(unittest.TestCase):

    # Tests for validate_title

    def test_validate_title(self):

        result = tickets.validate_title("   Wi-Fi is down   ")

        self.assertEqual(result, "Wi-Fi is down")



    def test_blank_title(self):

        with self.assertRaises(ValueError):

            tickets.validate_title("  ")



class TestValidateCategory(unittest.TestCase):

    # Tests for validate_category

    def test_validate_category(self):

        result = tickets.validate_category(VALID_CATEGORIES, "  NetWork   ")

        self.assertEqual(result, "Network")



    def test_whitespace_only_category_rejected(self):

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



    def test_empty_category_rejected(self):

        with self.assertRaises(ValueError):

            tickets.validate_category(VALID_CATEGORIES, "")

    def test_non_text_category_rejected(self):

        with self.assertRaises(ValueError):

            tickets.validate_category(VALID_CATEGORIES, None)



class TestValidateUrgency(unittest.TestCase):

    # Tests for validate_urgency

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





class TestValidateAffectedUsers(unittest.TestCase):

    # Tests for affected_users

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

    def test_affected_none_rejected(self):
        with self.assertRaises(ValueError):
            tickets.validate_affected_users(None)

class TestCalculatePriority(unittest.TestCase):

    # Tests for calculate_priority

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



class TestGenerateTicketId(unittest.TestCase):

    # Tests for generate_ticket_id

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



class TestCreateTicket(unittest.TestCase):

    # Tests for create_ticket

    def test_has_all_required_fields(self):

        ticket_list = []

        ticket = tickets.create_ticket(ticket_list, "Server down", "Hardware", "high", 5)

        required_keys = {

            "id",

            "title",

            "category",

            "urgency",

            "affected_users",

            "priority",

            "status",

            "assigned_to",

        }

        self.assertEqual(set(ticket.keys()), required_keys)



    def test_initial_defaults(self):

        ticket_list = []

        ticket = tickets.create_ticket(ticket_list, "Network slow", "Network", "low", 2)

        self.assertEqual(ticket["status"], "open")

        self.assertIsNone(ticket["assigned_to"])



    def test_stored_and_returned(self):

        ticket_list = []

        ticket = tickets.create_ticket(ticket_list, "Printer issue", "Hardware", "medium", 1)

        self.assertEqual(len(ticket_list), 1)

        self.assertEqual(ticket_list[0], ticket)



    def test_create_ticket_normalizes_fields(self):

        ticket_list = []

        ticket = tickets.create_ticket(ticket_list, "  Wi-Fi down ", "network", "HIGH", 4)

        self.assertEqual(ticket["title"], "Wi-Fi down")

        self.assertEqual(ticket["category"], "Network")

        self.assertEqual(ticket["urgency"], "high")



    def test_priority_is_calculated(self):

        ticket_list = []

        ticket = tickets.create_ticket(ticket_list, "Major outage", "Network", "high", 15)

        self.assertEqual(ticket["priority"], "critical")



    def test_string_affected_users_becomes_int(self):

        ticket_list = []

        ticket = tickets.create_ticket(ticket_list, "Bug fix", "Software", "low", "15")

        self.assertIsInstance(ticket["affected_users"], int)

        self.assertEqual(ticket["affected_users"], 15)



    def test_sequential_ids(self):

        ticket_list = []

        t1 = tickets.create_ticket(ticket_list, "First ticket", "Hardware", "low", 1)

        t2 = tickets.create_ticket(ticket_list, "Second ticket", "Software", "low", 1)

        self.assertEqual(t1["id"], "T001")

        self.assertEqual(t2["id"], "T002")



    def test_invalid_input_blank_title_stores_nothing(self):

        ticket_list = []

        with self.assertRaises(ValueError):

            tickets.create_ticket(ticket_list, "   ", "Hardware", "low", 1)

        self.assertEqual(len(ticket_list), 0)



    def test_invalid_input_invalid_category_stores_nothing(self):

        ticket_list = []

        with self.assertRaises(ValueError):

            tickets.create_ticket(ticket_list, "Valid Title", "Printer", "low", 1)

        self.assertEqual(len(ticket_list), 0)



    def test_invalid_input_invalid_urgency_stores_nothing(self):

        ticket_list = []

        with self.assertRaises(ValueError):

            tickets.create_ticket(ticket_list, "Valid Title", "Hardware", "urgent", 1)

        self.assertEqual(len(ticket_list), 0)



    def test_invalid_input_invalid_affected_users_stores_nothing(self):

        ticket_list = []

        with self.assertRaises(ValueError):

            tickets.create_ticket(ticket_list, "Valid Title", "Hardware", "low", 0)

        self.assertEqual(len(ticket_list), 0)



    def test_ids_unique_when_starting_from_loaded_records(self):

        ticket_list = [

            {

                "id": "T005",

                "title": "Old Ticket",

                "category": "Hardware",

                "urgency": "low",

                "affected_users": 1,

                "priority": "low",

                "status": "open",

                "assigned_to": None,

            }

        ]

        ticket = tickets.create_ticket(ticket_list, "New Ticket", "Software", "low", 1)

        self.assertEqual(ticket["id"], "T006")



class TestGetTicketById(unittest.TestCase):

    # Tests for get_ticket_by_id

    def test_finds_existing_ticket(self):

        ticket_list = [{"id": "T001", "title": "Server down"}]

        result = tickets.get_ticket_by_id(ticket_list, "T001")

        self.assertEqual(result["id"], "T001")

        self.assertEqual(result["title"], "Server down")



    def test_returns_actual_dictionary_not_copy(self):

        ticket_list = [{"id": "T001", "title": "Server down"}]

        result = tickets.get_ticket_by_id(ticket_list, "T001")

        result["title"] = "Updated Title"

        self.assertEqual(ticket_list[0]["title"], "Updated Title")



    def test_ticket_id_lookup_normalizes_whitespace_and_case(self):

        ticket_list = [{"id": "T001", "title": "Server down"}]

        result = tickets.get_ticket_by_id(ticket_list, "  t001  ")

        self.assertEqual(result["id"], "T001")



    def test_non_string_id_raises_value_error(self):

        ticket_list = [{"id": "T001", "title": "Server down"}]

        with self.assertRaises(ValueError):

            tickets.get_ticket_by_id(ticket_list, 1)



    def test_unknown_id_raises_value_error(self):

        ticket_list = [{"id": "T001", "title": "Server down"}]

        with self.assertRaises(ValueError):

            tickets.get_ticket_by_id(ticket_list, "T999")



class TestListTickets(unittest.TestCase):

    # Tests for list_tickets

    def test_returns_all_tickets_in_order(self):

        ticket_list = [

            {"id": "T001", "title": "First"},

            {"id": "T002", "title": "Second"},

            {"id": "T003", "title": "Third"},

        ]

        result = tickets.list_tickets(ticket_list)

        self.assertEqual(len(result), 3)

        self.assertEqual(result[0]["id"], "T001")

        self.assertEqual(result[1]["id"], "T002")

        self.assertEqual(result[2]["id"], "T003")



    def test_empty_list_returns_empty_list(self):

        ticket_list = []

        result = tickets.list_tickets(ticket_list)

        self.assertEqual(result, [])

        self.assertIsNot(result, ticket_list)



    def test_returns_new_list_original_unchanged(self):

        ticket_list = [

            {"id": "T001", "title": "First"},

            {"id": "T002", "title": "Second"},

        ]

        result = tickets.list_tickets(ticket_list)

        # Mutate the returned list

        result.append({"id": "T003", "title": "Third"})

        result.reverse()



        # Original list should remain unchanged in length and order

        self.assertEqual(len(ticket_list), 2)

        self.assertEqual(ticket_list[0]["id"], "T001")

        self.assertEqual(ticket_list[1]["id"], "T002")

    def test_modifying_listed_ticket_status_does_not_affect_storage(self):
        ticket_list = []
        tickets.create_ticket(ticket_list, "Server down", "Hardware", "high", 5)
        
        result = tickets.list_tickets(ticket_list)
        result[0]["status"] = "closed"
        
        self.assertEqual(ticket_list[0]["status"], "open")



if __name__ == "__main__":

    unittest.main()