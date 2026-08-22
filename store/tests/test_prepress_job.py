import os
import sys
import unittest

STORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if STORE_DIR not in sys.path:
    sys.path.insert(0, STORE_DIR)

from prepress.job import PrintJobValidationError, normalize_print_job


class PrintJobValidationTests(unittest.TestCase):
    def test_valid_job_normalizes_line_endings_and_optional_pieces(self):
        job = normalize_print_job("wedding-day-set", {
            "language": "de",
            "enabled_optional": ["program_day_2", "accommodation", "program_day_2"],
            "fields": {"coupleNames": "Anna & David", "venueAddress": "Line 1\r\nLine 2"},
            "labels": {"day_two": "Tag 2"},
        })
        self.assertEqual(job["language"], "de")
        self.assertEqual(job["fields"]["venueAddress"], "Line 1\nLine 2")
        self.assertEqual(job["enabled_optional"], ["accommodation", "program_day_2"])

    def test_unknown_customer_field_is_rejected(self):
        with self.assertRaises(PrintJobValidationError):
            normalize_print_job("wedding-day-set", {
                "fields": {"hidden_admin_field": "x"},
                "labels": {},
            })

    def test_unknown_optional_piece_is_rejected(self):
        with self.assertRaises(PrintJobValidationError):
            normalize_print_job("wedding-day-set", {
                "enabled_optional": ["program_day_3"],
                "fields": {},
                "labels": {},
            })

    def test_unsupported_language_is_rejected(self):
        with self.assertRaises(PrintJobValidationError):
            normalize_print_job("wedding-day-set", {
                "language": "xx",
                "fields": {},
                "labels": {},
            })

    def test_overlong_field_is_rejected(self):
        with self.assertRaises(PrintJobValidationError):
            normalize_print_job("wedding-day-set", {
                "fields": {"thankMessage": "x" * 601},
                "labels": {},
            })

    def test_nul_control_character_is_removed(self):
        job = normalize_print_job("wedding-day-set", {
            "fields": {"guestName": "Sophia\x00 Miller"},
            "labels": {},
        })
        self.assertEqual(job["fields"]["guestName"], "Sophia Miller")


if __name__ == "__main__":
    unittest.main()
