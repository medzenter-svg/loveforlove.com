import os
import sys
import tempfile
import unittest
from unittest import mock

STORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if STORE_DIR not in sys.path:
    sys.path.insert(0, STORE_DIR)

import app as store_app


class EditorDraftTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_patch = mock.patch.dict(os.environ, {"DRAFT_DB_PATH": os.path.join(self.tmp.name, "drafts.sqlite3")}, clear=False)
        self.db_patch.start()
        self.email = "buyer@example.com"
        self.token = store_app.make_access_token("draft-order-1", ["wedding-day-set"], self.email, dev_paid=True)
        self.base = f"/customize/{self.token}/wedding-day-set"

    def tearDown(self):
        self.db_patch.stop()
        self.tmp.cleanup()

    def _verified_client(self):
        client = store_app.app.test_client()
        response = client.post(f"/access/{self.token}", data={"email": self.email, "next": self.base}, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        return client

    def test_customer_can_edit_same_purchase_multiple_times(self):
        client = self._verified_client()
        url = self.base + "/draft"
        first = client.put(url, json={"state": {"weddingDate": "14 June 2027", "menu": "Menu A"}})
        second = client.put(url, json={"state": {"weddingDate": "21 June 2027", "menu": "Menu B"}})
        self.assertEqual(first.get_json()["revision"], 1)
        self.assertEqual(second.get_json()["revision"], 2)
        draft = client.get(url).get_json()["draft"]
        self.assertEqual(draft["revision"], 2)
        self.assertEqual(draft["state"]["weddingDate"], "21 June 2027")

    def test_same_order_resumes_on_another_browser_after_email_verification(self):
        first = self._verified_client()
        first.put(self.base + "/draft", json={"state": {"venueName": "New Venue", "weddingTime": "6:00 PM"}})
        second = store_app.app.test_client()
        self.assertEqual(second.get(self.base + "/draft").status_code, 403)
        verify = second.post(f"/access/{self.token}", data={"email": self.email, "next": self.base}, follow_redirects=False)
        self.assertEqual(verify.status_code, 302)
        state = second.get(self.base + "/draft").get_json()["draft"]["state"]
        self.assertEqual(state["venueName"], "New Venue")
        self.assertEqual(state["weddingTime"], "6:00 PM")

    def test_previous_version_can_be_restored(self):
        client = self._verified_client()
        url = self.base + "/draft"
        client.put(url, json={"state": {"weddingDate": "First date"}})
        client.put(url, json={"state": {"weddingDate": "Second date"}})
        restored = client.post(url + "/restore/1").get_json()
        self.assertEqual(restored["state"]["weddingDate"], "First date")
        self.assertEqual(restored["revision"], 3)


if __name__ == "__main__":
    unittest.main()
