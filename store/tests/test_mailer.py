import os
import sys
import unittest

STORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if STORE_DIR not in sys.path:
    sys.path.insert(0, STORE_DIR)

from mailer import build_order_access_message


class MailerTests(unittest.TestCase):
    def test_access_email_contains_order_products_and_protected_link(self):
        message = build_order_access_message(
            "buyer@example.com",
            "order-123",
            "https://loveforlove.com/access/signed-token?next=%2Fsuccess",
            ["Editable Complete Wedding Suite", "Save the Date"],
        )
        body = message.get_content()
        self.assertIn("order-123", body)
        self.assertIn("Editable Complete Wedding Suite", body)
        self.assertIn("Save the Date", body)
        self.assertIn("https://loveforlove.com/access/signed-token", body)
        self.assertIn("same email address used during checkout", body)
        self.assertIn("continue editing", body)

    def test_access_email_has_no_attachments(self):
        message = build_order_access_message(
            "buyer@example.com",
            "order-123",
            "https://loveforlove.com/access/token",
            ["Editable Complete Wedding Suite"],
        )
        self.assertFalse(message.is_multipart())
        self.assertEqual(list(message.iter_attachments()), [])


if __name__ == "__main__":
    unittest.main()
