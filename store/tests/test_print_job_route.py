import os
import sys
import unittest

STORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if STORE_DIR not in sys.path:
    sys.path.insert(0, STORE_DIR)

import app as store_app


class PrintJobRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = store_app.app.test_client()
        self.email = "buyer@example.com"
        self.token = store_app.make_access_token(
            "test-order",
            ["wedding-day-set"],
            self.email,
            dev_paid=True,
        )
        self.url = f"/customize/{self.token}/wedding-day-set/print-job/validate"
        payload = store_app.read_access_token(self.token)
        with self.client.session_transaction() as flask_session:
            flask_session["verified_orders"] = {
                payload["order_id"]: payload["customer_email_hash"]
            }

    def test_full_default_package_reports_60_professional_files(self):
        response = self.client.post(self.url, json={
            "language": "en",
            "fields": {"coupleNames": "Emma & James"},
            "labels": {"invitation": "Wedding Invitation"},
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["printable_pieces"], 15)
        self.assertEqual(data["professional_pdf_files"], 60)
        self.assertFalse(data["professional_print_package_ready"])

    def test_core_only_package_reports_32_professional_files(self):
        response = self.client.post(self.url, json={
            "language": "en",
            "enabled_optional": [],
            "fields": {},
            "labels": {},
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["printable_pieces"], 8)
        self.assertEqual(data["professional_pdf_files"], 32)

    def test_unknown_field_is_rejected(self):
        response = self.client.post(self.url, json={
            "language": "en",
            "fields": {"unexpected": "value"},
            "labels": {},
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["ok"])

    def test_unverified_browser_is_rejected(self):
        fresh_client = store_app.app.test_client()
        response = fresh_client.post(self.url, json={
            "language": "en",
            "fields": {},
            "labels": {},
        })
        self.assertEqual(response.status_code, 403)

    def test_wrong_product_access_is_rejected(self):
        token = store_app.make_access_token(
            "test-order",
            ["love-coupon-book"],
            self.email,
            dev_paid=True,
        )
        response = self.client.post(
            f"/customize/{token}/wedding-day-set/print-job/validate",
            json={"fields": {}, "labels": {}},
        )
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
