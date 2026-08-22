import os
import sys
import tempfile
import unittest
from unittest import mock

STORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if STORE_DIR not in sys.path:
    sys.path.insert(0, STORE_DIR)

import app as store_app
import order_store
from persistent_access import install_persistent_paid_access


class PersistentAccessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env_patch = mock.patch.dict(
            os.environ,
            {"DATABASE_URL": "", "DRAFT_DB_PATH": os.path.join(self.tmp.name, "orders.sqlite3")},
            clear=False,
        )
        self.env_patch.start()
        self.original = store_app.paid_access

    def tearDown(self):
        store_app.paid_access = self.original
        self.env_patch.stop()
        self.tmp.cleanup()

    def test_persisted_paid_order_does_not_need_new_stripe_lookup(self):
        order_store.record_paid_order(
            "order-longterm",
            "cs_paid_1",
            "buyer@example.com",
            ["wedding-day-set"],
        )
        token = store_app.make_access_token(
            "order-longterm",
            ["wedding-day-set"],
            "buyer@example.com",
            stripe_session_id="cs_paid_1",
        )
        install_persistent_paid_access(store_app)

        with mock.patch("app.stripe.checkout.Session.retrieve", side_effect=RuntimeError("Stripe unavailable")):
            with store_app.app.test_request_context("/"):
                payload = store_app.paid_access(token, "wedding-day-set")

        self.assertEqual(payload["order_id"], "order-longterm")

    def test_changed_email_or_session_in_token_is_rejected(self):
        order_store.record_paid_order(
            "order-longterm",
            "cs_paid_1",
            "buyer@example.com",
            ["wedding-day-set"],
        )
        bad_token = store_app.make_access_token(
            "order-longterm",
            ["wedding-day-set"],
            "other@example.com",
            stripe_session_id="cs_paid_1",
        )
        install_persistent_paid_access(store_app)

        with store_app.app.test_request_context("/"):
            with self.assertRaises(Exception):
                store_app.paid_access(bad_token, "wedding-day-set")


if __name__ == "__main__":
    unittest.main()
