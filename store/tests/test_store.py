import unittest

from app import app, verified_catalog


class StoreSafetyTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, SECRET_KEY="test-only")
        self.client = app.test_client()

    def test_public_pages_render(self):
        for path in ("/", "/shop", "/cart", "/cancel"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")

    def test_legacy_drafts_cannot_enter_checkout(self):
        self.assertEqual(verified_catalog(), [])
        self.assertEqual(self.client.get("/product/invitation-suite").status_code, 404)
        self.assertEqual(self.client.post("/cart/add/invitation-suite").status_code, 404)

    def test_language_switch_and_hebrew_direction(self):
        russian = self.client.post("/language/ru", data={"next": "/"}, follow_redirects=True)
        self.assertIn("История любви".encode(), russian.data)
        hebrew = self.client.post("/language/he", data={"next": "/shop"}, follow_redirects=True)
        self.assertIn(b'dir="rtl"', hebrew.data)

    def test_language_redirect_rejects_external_target(self):
        response = self.client.post("/language/de", data={"next": "https://example.com"})
        self.assertEqual(response.headers["Location"], "/")

    def test_empty_checkout_is_safe(self):
        response = self.client.post("/checkout")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/cart"))


if __name__ == "__main__":
    unittest.main()
