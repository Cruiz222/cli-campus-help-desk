import unittest
from campusflow import tickets 
from campusflow.tickets import (
    VALID_CATEGORIES
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
    
    def test_variants_normalized(self):
        variant_categories = ["hArdWare", "SOFTWARE", "other"]
        for each_category in variant_categories:
            result = tickets.validate_category(VALID_CATEGORIES, each_category)
            self.assertIn(result, VALID_CATEGORIES)

    def test_trimmed_spaces(self):
        result = tickets.validate_category(VALID_CATEGORIES, "  other  ")
        self.assertEqual(result, "Other")

    def test_invalid_category_rejected(self):
        with self.assertRaises(ValueError):
            tickets.validate_category(VALID_CATEGORIES, "Printer")

    def test_blank_rejected(self):
        with self.assertRaises(ValueError):
            tickets.validate_category(VALID_CATEGORIES, "")
    
    def test_non_text_rejected(self):
        with self.assertRaises(ValueError):
            tickets.validate_category(VALID_CATEGORIES, None)
    


if __name__ == "__main__":
    unittest.main()
