import os
import sys
import unittest
from unittest import mock

STORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if STORE_DIR not in sys.path:
    sys.path.insert(0, STORE_DIR)

import startup_check


class StartupCheckTests(unittest.TestCase):
    def test_preview_mode_allows_local_storage(self):
        with mock.patch.dict(os.environ, {"STRIPE_SECRET_KEY": "", "SECRET_KEY": "dev-secret-change-me"}, clear=False), \
             mock.patch("startup_check.draft_store_healthcheck", return_value={"ok": True, "mode": "sqlite"}):
            self.assertEqual(startup_check.main(), 0)

    def test_live_payments_reject_default_secret(self):
        with mock.patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_live_test", "SECRET_KEY": "dev-secret-change-me"}, clear=False):
            self.assertEqual(startup_check.main(), 1)

    def test_live_payments_reject_nonpersistent_draft_storage(self):
        with mock.patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_live_test", "SECRET_KEY": "strong-secret"}, clear=False), \
             mock.patch("startup_check.production_draft_storage_ready", return_value=False):
            self.assertEqual(startup_check.main(), 1)

    def test_live_payments_accept_persistent_database_and_healthcheck(self):
        with mock.patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_live_test", "SECRET_KEY": "strong-secret"}, clear=False), \
             mock.patch("startup_check.production_draft_storage_ready", return_value=True), \
             mock.patch("startup_check.draft_store_healthcheck", return_value={"ok": True, "mode": "postgresql"}):
            self.assertEqual(startup_check.main(), 0)


if __name__ == "__main__":
    unittest.main()
