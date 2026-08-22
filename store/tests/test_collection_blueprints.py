import os
import sys
import unittest

STORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if STORE_DIR not in sys.path:
    sys.path.insert(0, STORE_DIR)

from collection_blueprints import COLLECTION_BLUEPRINTS


EXPECTED_WEDDING_CODES = {
    "paris-editorial",
    "amalfi-luce",
    "monaco-regatta",
    "como-sereno",
    "provence-rose",
    "santorini-aegean",
    "riviera-garden",
    "vienna-champagne",
}


class CollectionBlueprintTests(unittest.TestCase):
    def test_wedding_collection_codes_are_complete_and_unique(self):
        wedding = [item for item in COLLECTION_BLUEPRINTS if item["occasion"] == "Weddings"]
        codes = [item["code"] for item in wedding]
        self.assertEqual(set(codes), EXPECTED_WEDDING_CODES)
        self.assertEqual(len(codes), len(set(codes)))

    def test_wedding_collections_are_real_design_systems_not_color_swaps(self):
        wedding = [item for item in COLLECTION_BLUEPRINTS if item["occasion"] == "Weddings"]
        signatures = set()
        for item in wedding:
            self.assertTrue(item.get("style"))
            self.assertTrue(item.get("signature"))
            self.assertTrue(item.get("prepress_theme"))
            self.assertGreaterEqual(len(item.get("palette") or []), 3)
            signatures.add(item["signature"])
        self.assertEqual(len(signatures), len(wedding))

    def test_wedding_palettes_do_not_use_black_as_a_design_color(self):
        wedding = [item for item in COLLECTION_BLUEPRINTS if item["occasion"] == "Weddings"]
        for item in wedding:
            palette = " ".join(item.get("palette") or []).lower()
            self.assertNotIn("black", palette, item["code"])

    def test_only_current_paris_prototype_claims_prepress_passed(self):
        wedding = [item for item in COLLECTION_BLUEPRINTS if item["occasion"] == "Weddings"]
        passed = [item["code"] for item in wedding if item.get("status") == "prototype_prepress_passed"]
        self.assertEqual(passed, ["paris-editorial"])


if __name__ == "__main__":
    unittest.main()
