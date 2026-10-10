import unittest
from campusflow import tickets 
from campusflow.tickets import (
    VALID_CATEGORIES,
    VALID_URGENCIES
)


class TestValidateTitle(unittest.TestCase):

    def test_validate_title(self):
        result = tickets.validate_title("   Wi-Fi is down   ")
        self.assertEqual(result, "Wi-Fi is down")

    def test_blank_title(self):
        with self.assertRaises(ValueError):
            tickets.validate_title("  ")

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


if __name__ == "__main__":
    unittest.main()
