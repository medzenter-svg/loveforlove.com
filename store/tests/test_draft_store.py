import os
import sys
import tempfile
import unittest
from unittest import mock

STORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if STORE_DIR not in sys.path:
    sys.path.insert(0, STORE_DIR)

import draft_store


class DraftStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.patch = mock.patch.dict(
            os.environ,
            {
                "DATABASE_URL": "",
                "DRAFT_DB_PATH": os.path.join(self.tmp.name, "drafts.sqlite3"),
            },
            clear=False,
        )
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()

    def test_revision_metadata_is_not_persisted_as_customer_state(self):
        saved = draft_store.save_draft(
            "order-1",
            "wedding-day-set",
            {"weddingDate": "14 June", draft_store.DRAFT_REVISION_KEY: 0},
        )
        self.assertEqual(saved["revision"], 1)
        loaded = draft_store.load_draft("order-1", "wedding-day-set")
        self.assertNotIn(draft_store.DRAFT_REVISION_KEY, loaded["state"])

    def test_stale_device_cannot_overwrite_newer_revision(self):
        draft_store.save_draft(
            "order-1",
            "wedding-day-set",
            {"weddingDate": "First", draft_store.DRAFT_REVISION_KEY: 0},
        )
        draft_store.save_draft(
            "order-1",
            "wedding-day-set",
            {"weddingDate": "Second", draft_store.DRAFT_REVISION_KEY: 1},
        )

        with self.assertRaises(draft_store.DraftConflictError) as caught:
            draft_store.save_draft(
                "order-1",
                "wedding-day-set",
                {"weddingDate": "Stale overwrite", draft_store.DRAFT_REVISION_KEY: 1},
            )
        self.assertEqual(caught.exception.current_revision, 2)
        self.assertEqual(
            draft_store.load_draft("order-1", "wedding-day-set")["state"]["weddingDate"],
            "Second",
        )

    def test_history_keeps_only_recent_20_versions(self):
        current = 0
        for number in range(1, 26):
            saved = draft_store.save_draft(
                "order-1",
                "wedding-day-set",
                {"tableNumber": str(number), draft_store.DRAFT_REVISION_KEY: current},
            )
            current = saved["revision"]

        revisions = draft_store.list_draft_revisions("order-1", "wedding-day-set")
        self.assertEqual(len(revisions), 20)
        self.assertEqual(revisions[0]["revision"], 25)
        self.assertEqual(revisions[-1]["revision"], 6)


if __name__ == "__main__":
    unittest.main()
