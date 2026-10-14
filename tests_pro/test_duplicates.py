import unittest

from campusflow_pro.duplicates import (
    normalize_title,
    find_duplicates,
    confirm_creation,
)


class TestDuplicates(unittest.TestCase):

    def setUp(self):
        self.existing = [
            {"id": 1, "title": "Internet connection is not working",
             "category": "Network", "status": "open"},
            {"id": 2, "title": "Printer problem",
             "category": "Hardware", "status": "resolved"},
            {"id": 3, "title": "Internet connection is not working",
             "category": "Network", "status": "resolved"},
        ]
        self.new = {"title": "  INTERNET   Connection IS NOT WORKING ",
                    "category": "network"}

    def test_normalize_title(self):
        self.assertEqual(
            normalize_title("  INTERNET   Connection  "),
            "internet connection",
        )

    def test_non_string_title_rejected(self):
        with self.assertRaises(ValueError):
            normalize_title(None)

    def test_finds_unresolved_duplicate_only(self):
        matches = find_duplicates(self.new, self.existing)
        self.assertEqual([m["id"] for m in matches], [1])

    def test_resolved_ticket_is_not_duplicate(self):
        new = {"title": "Printer problem", "category": "Hardware"}
        self.assertEqual(find_duplicates(new, self.existing), [])

    def test_different_category_is_not_duplicate(self):
        new = {"title": "Internet connection is not working",
               "category": "Software"}
        self.assertEqual(find_duplicates(new, self.existing), [])

    def test_confirm_creation_declined(self):
        self.assertFalse(confirm_creation(
            self.new, self.existing,
            input_fn=lambda _: "n", output_fn=lambda _: None))

    def test_confirm_creation_accepted(self):
        self.assertTrue(confirm_creation(
            self.new, self.existing,
            input_fn=lambda _: "y", output_fn=lambda _: None))

    def test_no_duplicate_skips_prompt(self):
        new = {"title": "Projector broken", "category": "Hardware"}
        self.assertTrue(confirm_creation(
            new, self.existing,
            input_fn=lambda _: self.fail("should not prompt"),
            output_fn=lambda _: None))


if __name__ == "__main__":
    unittest.main()