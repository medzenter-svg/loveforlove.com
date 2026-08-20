import os
import sys
import unittest

STORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if STORE_DIR not in sys.path:
    sys.path.insert(0, STORE_DIR)

from collection_blueprints import COLLECTION_BLUEPRINTS
from prepress.design_themes import (
    DEFAULT_PREPRESS_THEME,
    PrepressThemeError,
    WEDDING_PREPRESS_THEMES,
    get_prepress_theme,
    get_prototype_theme,
    implemented_theme_codes,
)


PROTOTYPE_CODES = {
    "amalfi-luce",
    "monaco-regatta",
    "como-sereno",
    "provence-rose",
    "santorini-aegean",
    "riviera-garden",
    "vienna-champagne",
}


class PrepressThemeTests(unittest.TestCase):
    def test_only_paris_editorial_is_currently_implemented(self):
        self.assertEqual(DEFAULT_PREPRESS_THEME, "paris-editorial")
        self.assertEqual(implemented_theme_codes(), {"paris-editorial"})
        self.assertTrue(get_prepress_theme("paris-editorial")["implemented"])

    def test_every_unapproved_theme_fails_closed_for_customer_export(self):
        for code, theme in WEDDING_PREPRESS_THEMES.items():
            if theme.get("implemented"):
                continue
            with self.assertRaises(PrepressThemeError, msg=code):
                get_prepress_theme(code, require_implemented=True)

    def test_seven_design_locked_themes_allow_invitation_prototype_only(self):
        for code in PROTOTYPE_CODES:
            theme = get_prototype_theme(code, "invitation")
            self.assertTrue(theme["prototype_ready"], code)
            self.assertFalse(theme["implemented"], code)
            self.assertEqual(theme["prototype_piece"], "invitation", code)
            with self.assertRaises(PrepressThemeError, msg=code):
                get_prototype_theme(code, "menu")

    def test_every_wedding_blueprint_has_a_registered_prepress_theme(self):
        wedding = [item for item in COLLECTION_BLUEPRINTS if item["occasion"] == "Weddings"]
        for item in wedding:
            self.assertIn(item["prepress_theme"], WEDDING_PREPRESS_THEMES)

    def test_unknown_theme_is_rejected(self):
        with self.assertRaises(PrepressThemeError):
            get_prepress_theme("not-a-real-theme")


if __name__ == "__main__":
    unittest.main()
