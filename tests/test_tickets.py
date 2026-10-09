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

if __name__ == "__main__":
    unittest.main()
