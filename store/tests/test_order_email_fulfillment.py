import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest import mock

STORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if STORE_DIR not in sys.path:
    sys.path.insert(0, STORE_DIR)

import app as store_app
import order_store
import payments


class OrderEmailFulfillmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env_patch = mock.patch.dict(
            os.environ,
            {
                "DATABASE_URL": "",
                "DRAFT_DB_PATH": os.path.join(self.tmp.name, "orders.sqlite3"),
                "SMTP_HOST": "smtp.example.com",
                "SMTP_FROM": "orders@loveforlove.com",
            },
            clear=False,
        )
        self.env_patch.start()
        self.session = SimpleNamespace(
            id="cs_test_123",
            payment_status="paid",
            metadata={
                "order_id": "order-mail-1",
                "slugs": "wedding-day-set",
            },
            customer_details=SimpleNamespace(email="buyer@example.com"),
            customer_email=None,
        )

    def tearDown(self):
        self.env_patch.stop()
        self.tmp.cleanup()

    def test_paid_order_is_persisted_and_access_email_is_sent_once(self):
        with store_app.app.test_request_context("/stripe/webhook"), \
             mock.patch("payments.mail_configured", return_value=True), \
             mock.patch("payments.send_order_access_email") as sender:
            first = payments.fulfill_paid_session(self.session)
            second = payments.fulfill_paid_session(self.session)

        self.assertEqual(first["order_id"], "order-mail-1")
        self.assertIn("/access/", first["access_url"])
        self.assertEqual(sender.call_count, 1)
        self.assertFalse(second["email_sent"])

        order = order_store.get_paid_order("order-mail-1")
        self.assertEqual(order["customer_email"], "buyer@example.com")
        self.assertEqual(order["slugs"], ["wedding-day-set"])
        self.assertEqual(order["access_email_status"], order_store.EMAIL_SENT)
        self.assertEqual(order["access_email_attempts"], 1)

    def test_failed_email_is_retryable(self):
        with store_app.app.test_request_context("/stripe/webhook"), \
             mock.patch("payments.mail_configured", return_value=True), \
             mock.patch("payments.send_order_access_email", side_effect=RuntimeError("smtp down")):
            with self.assertRaises(RuntimeError):
                payments.fulfill_paid_session(self.session)

        failed = order_store.get_paid_order("order-mail-1")
        self.assertEqual(failed["access_email_status"], order_store.EMAIL_FAILED)
        self.assertEqual(failed["access_email_attempts"], 1)

        with store_app.app.test_request_context("/stripe/webhook"), \
             mock.patch("payments.mail_configured", return_value=True), \
             mock.patch("payments.send_order_access_email") as sender:
            retried = payments.fulfill_paid_session(self.session)

        self.assertTrue(retried["email_sent"])
        self.assertEqual(sender.call_count, 1)
        sent = order_store.get_paid_order("order-mail-1")
        self.assertEqual(sent["access_email_status"], order_store.EMAIL_SENT)
        self.assertEqual(sent["access_email_attempts"], 2)

    def test_abandoned_sending_reservation_is_recoverable_after_lease(self):
        start = datetime(2026, 8, 20, 10, 0, tzinfo=timezone.utc)
        with mock.patch("order_store._now_dt", return_value=start):
            order_store.record_paid_order(
                "order-mail-1",
                "cs_test_123",
                "buyer@example.com",
                ["wedding-day-set"],
            )
            self.assertTrue(order_store.begin_access_email_delivery("order-mail-1"))

        five_minutes_later = start + timedelta(minutes=5)
        with mock.patch("order_store._now_dt", return_value=five_minutes_later):
            # A duplicate payment event must not refresh the active email lease.
            order_store.record_paid_order(
                "order-mail-1",
                "cs_test_123",
                "buyer@example.com",
                ["wedding-day-set"],
            )
            self.assertFalse(order_store.begin_access_email_delivery("order-mail-1"))

        eleven_minutes_later = start + timedelta(minutes=11)
        with mock.patch("order_store._now_dt", return_value=eleven_minutes_later):
            order_store.record_paid_order(
                "order-mail-1",
                "cs_test_123",
                "buyer@example.com",
                ["wedding-day-set"],
            )
            self.assertTrue(order_store.begin_access_email_delivery("order-mail-1"))

        order = order_store.get_paid_order("order-mail-1")
        self.assertEqual(order["access_email_status"], order_store.EMAIL_SENDING)
        self.assertEqual(order["access_email_attempts"], 2)

    def test_unpaid_session_is_never_fulfilled(self):
        self.session.payment_status = "unpaid"
        with store_app.app.test_request_context("/stripe/webhook"), \
             mock.patch("payments.send_order_access_email") as sender:
            result = payments.fulfill_paid_session(self.session)
        self.assertIsNone(result)
        sender.assert_not_called()
        self.assertIsNone(order_store.get_paid_order("order-mail-1"))


if __name__ == "__main__":
    unittest.main()
