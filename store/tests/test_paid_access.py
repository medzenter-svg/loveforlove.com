import os
import sys
import unittest

STORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if STORE_DIR not in sys.path:
    sys.path.insert(0, STORE_DIR)

import app as store_app


class PaidAccessTests(unittest.TestCase):
    def setUp(self):
        self.email = "Buyer@Example.com"
        self.token = store_app.make_access_token(
            "order-123",
            ["wedding-day-set"],
            self.email,
            dev_paid=True,
        )

    def test_token_contains_email_hash_not_plain_email(self):
        payload = store_app.read_access_token(self.token)
        self.assertNotIn("customer_email", payload)
        self.assertEqual(
            payload["customer_email_hash"],
            store_app.email_digest("buyer@example.com"),
        )
        self.assertNotIn("buyer@example.com", self.token.lower())

    def test_fresh_browser_is_redirected_to_email_verification(self):
        client = store_app.app.test_client()
        response = client.get(
            f"/customize/{self.token}/wedding-day-set",
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/access/", response.headers["Location"])

    def test_wrong_email_does_not_unlock_order(self):
        client = store_app.app.test_client()
        response = client.post(
            f"/access/{self.token}",
            data={"email": "wrong@example.com", "next": f"/customize/{self.token}/wedding-day-set"},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"does not match", response.data)

        payload = store_app.read_access_token(self.token)
        with client.session_transaction() as flask_session:
            verified = flask_session.get("verified_orders") or {}
            self.assertNotIn(payload["order_id"], verified)

    def test_correct_email_unlocks_same_order(self):
        client = store_app.app.test_client()
        next_path = f"/customize/{self.token}/wedding-day-set"
        response = client.post(
            f"/access/{self.token}",
            data={"email": " buyer@example.com ", "next": next_path},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith(next_path))

        payload = store_app.read_access_token(self.token)
        with client.session_transaction() as flask_session:
            verified = flask_session.get("verified_orders") or {}
            self.assertEqual(
                verified[payload["order_id"]],
                payload["customer_email_hash"],
            )

    def test_order_id_is_part_of_browser_verification_scope(self):
        client = store_app.app.test_client()
        token_a = store_app.make_access_token(
            "order-a", ["wedding-day-set"], "buyer@example.com", dev_paid=True
        )
        token_b = store_app.make_access_token(
            "order-b", ["wedding-day-set"], "buyer@example.com", dev_paid=True
        )
        payload_a = store_app.read_access_token(token_a)
        with client.session_transaction() as flask_session:
            flask_session["verified_orders"] = {
                payload_a["order_id"]: payload_a["customer_email_hash"]
            }

        response = client.get(
            f"/customize/{token_b}/wedding-day-set",
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/access/", response.headers["Location"])


if __name__ == "__main__":
    unittest.main()
