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


PROTOTYPE_CODES = {"amalfi-luce"}


class PrepressThemeTests(unittest.TestCase):
    def test_only_paris_editorial_is_currently_implemented(self):
        self.assertEqual(DEFAULT_PREPRESS_THEME, "paris-editorial")
        self.assertEqual(implemented_theme_codes(), {"paris-editorial"})
        self.assertTrue(get_prepress_theme("paris-editorial")["implemented"])

    def test_planned_wedding_themes_fail_closed_for_customer_export(self):
        for code, theme in WEDDING_PREPRESS_THEMES.items():
            if theme.get("implemented"):
                continue
            with self.assertRaises(PrepressThemeError, msg=code):
                get_prepress_theme(code, require_implemented=True)

    def test_amalfi_design_locked_theme_allows_invitation_prototype_only(self):
        theme = get_prototype_theme("amalfi-luce", "invitation")
        self.assertTrue(theme["prototype_ready"])
        self.assertFalse(theme["implemented"])
        self.assertEqual(theme["prototype_piece"], "invitation")
        with self.assertRaises(PrepressThemeError):
            get_prototype_theme("amalfi-luce", "menu")

    def test_other_planned_themes_have_no_prototype_path_yet(self):
        for code, theme in WEDDING_PREPRESS_THEMES.items():
            if code == "paris-editorial" or code in PROTOTYPE_CODES:
                continue
            self.assertFalse(theme.get("prototype_ready"), code)
            with self.assertRaises(PrepressThemeError, msg=code):
                get_prototype_theme(code, "invitation")

    def test_every_wedding_blueprint_has_a_registered_prepress_theme(self):
        wedding = [item for item in COLLECTION_BLUEPRINTS if item["occasion"] == "Weddings"]
        for item in wedding:
            self.assertIn(item["prepress_theme"], WEDDING_PREPRESS_THEMES)

    def test_unknown_theme_is_rejected(self):
        with self.assertRaises(PrepressThemeError):
            get_prepress_theme("not-a-real-theme")


if __name__ == "__main__":
    unittest.main()
