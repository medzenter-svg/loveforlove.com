import os
import sys
import unittest

STORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if STORE_DIR not in sys.path:
    sys.path.insert(0, STORE_DIR)

from print_package import OPTIONAL_PIECES, PIECE_ORDER, build_manifest, expected_filename
from print_piece_specs import PRINT_PIECE_SPECS
from products import PRODUCTS_BY_SLUG, is_sellable_product


class PrintPackageTests(unittest.TestCase):
    def test_full_suite_has_15_pieces_and_60_professional_pdfs(self):
        manifest = build_manifest("wedding-day-set")
        self.assertEqual(len(PIECE_ORDER), 15)
        self.assertEqual(len(manifest), 60)
        self.assertEqual(len({item["piece"] for item in manifest}), 15)

    def test_core_only_suite_has_8_pieces_and_32_professional_pdfs(self):
        manifest = build_manifest("wedding-day-set", enabled_optional=set())
        self.assertEqual(len(PIECE_ORDER) - len(OPTIONAL_PIECES), 8)
        self.assertEqual(len(manifest), 32)
        self.assertFalse(any(item["optional"] for item in manifest))

    def test_each_piece_has_both_size_families(self):
        for family_name, family in PRINT_PIECE_SPECS.items():
            with self.subTest(family=family_name):
                self.assertEqual(set(family["pieces"]), set(PIECE_ORDER))

    def test_envelopes_are_landscape(self):
        metric = PRINT_PIECE_SPECS["international_metric"]["pieces"]["envelope"]["trim_mm"]
        north_america = PRINT_PIECE_SPECS["north_america"]["pieces"]["envelope"]["trim_in"]
        self.assertGreater(metric[0], metric[1])
        self.assertGreater(north_america[0], north_america[1])

    def test_filename_is_stable_and_explicit(self):
        name = expected_filename(
            "wedding-day-set",
            "program_day_2",
            "north_america",
            "pdfx4_worldwide",
        )
        self.assertEqual(
            name,
            "wedding-day-set__program_day_2__NA__PDFX4.pdf",
        )

    def test_editable_suite_cannot_sell_before_professional_package_is_ready(self):
        product = PRODUCTS_BY_SLUG["wedding-day-set"]
        self.assertTrue(product["editable"])
        self.assertFalse(product["professional_print_package_ready"])
        self.assertFalse(is_sellable_product(product))

    def test_legacy_wedding_print_products_are_also_gated(self):
        for slug in ["save-the-date", "invitation-suite", "monogram-pack", "welcome-sign-set"]:
            with self.subTest(slug=slug):
                self.assertFalse(is_sellable_product(PRODUCTS_BY_SLUG[slug]))

    def test_non_wedding_gift_is_not_forced_through_wedding_prepress_gate(self):
        self.assertTrue(is_sellable_product(PRODUCTS_BY_SLUG["love-coupon-book"]))


if __name__ == "__main__":
    unittest.main()
