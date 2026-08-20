import os
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock
from urllib.parse import urlparse

STORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if STORE_DIR not in sys.path:
    sys.path.insert(0, STORE_DIR)

import app as store_app
import order_store
import payments
from persistent_access import install_persistent_paid_access


class PaidCustomerJourneyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env_patch = mock.patch.dict(
            os.environ,
            {
                "DATABASE_URL": "",
                "DRAFT_DB_PATH": os.path.join(self.tmp.name, "journey.sqlite3"),
                "SMTP_HOST": "smtp.example.com",
                "SMTP_FROM": "orders@loveforlove.com",
            },
            clear=False,
        )
        self.env_patch.start()
        self.original_paid_access = store_app.paid_access
        self.checkout_session = SimpleNamespace(
            id="cs_paid_journey_1",
            payment_status="paid",
            metadata={
                "order_id": "journey-order-1",
                "slugs": "wedding-day-set",
            },
            customer_details=SimpleNamespace(email="buyer@example.com"),
            customer_email=None,
        )

    def tearDown(self):
        store_app.paid_access = self.original_paid_access
        self.env_patch.stop()
        self.tmp.cleanup()

    def test_paid_customer_receives_link_verifies_email_and_resumes_saved_edit(self):
        captured = {}

        def capture_email(customer_email, order_id, access_url, product_names):
            captured.update({
                "customer_email": customer_email,
                "order_id": order_id,
                "access_url": access_url,
                "product_names": list(product_names),
            })

        with store_app.app.test_request_context("/stripe/webhook"), \
             mock.patch("payments.mail_configured", return_value=True), \
             mock.patch("payments.send_order_access_email", side_effect=capture_email):
            fulfillment = payments.fulfill_paid_session(self.checkout_session)

        self.assertTrue(fulfillment["email_sent"])
        self.assertEqual(captured["customer_email"], "buyer@example.com")
        self.assertEqual(captured["order_id"], "journey-order-1")
        self.assertIn("Editable Complete Wedding Suite", captured["product_names"])

        paid_order = order_store.get_paid_order("journey-order-1")
        self.assertEqual(paid_order["access_email_status"], order_store.EMAIL_SENT)

        install_persistent_paid_access(store_app)
        access_path = urlparse(captured["access_url"]).path
        access_query = urlparse(captured["access_url"]).query
        access_request = access_path + ("?" + access_query if access_query else "")

        first_browser = store_app.app.test_client()
        access_page = first_browser.get(access_request)
        self.assertEqual(access_page.status_code, 200)
        self.assertIn(b"journey-order-1", access_page.data)

        wrong_email = first_browser.post(
            access_path,
            data={"email": "wrong@example.com"},
            follow_redirects=False,
        )
        self.assertEqual(wrong_email.status_code, 200)
        self.assertIn(b"does not match", wrong_email.data)

        verified = first_browser.post(
            access_path,
            data={"email": "buyer@example.com"},
            follow_redirects=False,
        )
        self.assertEqual(verified.status_code, 302)

        token = fulfillment["access_token"]
        editor_path = f"/customize/{token}/wedding-day-set"
        editor = first_browser.get(editor_path)
        self.assertEqual(editor.status_code, 200)

        draft_path = editor_path + "/draft"
        saved = first_browser.put(
            draft_path,
            json={
                "state": {
                    "weddingDate": "14 June 2027",
                    "venueName": "Villa One",
                    "__draft_expected_revision": 0,
                }
            },
        )
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.get_json()["revision"], 1)

        second_browser = store_app.app.test_client()
        locked = second_browser.get(editor_path, follow_redirects=False)
        self.assertEqual(locked.status_code, 302)
        self.assertIn("/access/", locked.headers["Location"])

        second_browser.post(
            access_path,
            data={"email": "buyer@example.com", "next": editor_path},
            follow_redirects=False,
        )
        resumed = second_browser.get(draft_path)
        self.assertEqual(resumed.status_code, 200)
        draft = resumed.get_json()["draft"]
        self.assertEqual(draft["revision"], 1)
        self.assertEqual(draft["state"]["weddingDate"], "14 June 2027")
        self.assertEqual(draft["state"]["venueName"], "Villa One")

        changed = second_browser.put(
            draft_path,
            json={
                "state": {
                    "weddingDate": "21 June 2027",
                    "venueName": "Villa Two",
                    "__draft_expected_revision": 1,
                }
            },
        )
        self.assertEqual(changed.status_code, 200)
        self.assertEqual(changed.get_json()["revision"], 2)

        latest = first_browser.get(draft_path).get_json()["draft"]
        self.assertEqual(latest["revision"], 2)
        self.assertEqual(latest["state"]["venueName"], "Villa Two")


if __name__ == "__main__":
    unittest.main()
