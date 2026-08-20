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
    implemented_theme_codes,
)


class PrepressThemeTests(unittest.TestCase):
    def test_only_paris_editorial_is_currently_implemented(self):
        self.assertEqual(DEFAULT_PREPRESS_THEME, "paris-editorial")
        self.assertEqual(implemented_theme_codes(), {"paris-editorial"})
        self.assertTrue(get_prepress_theme("paris-editorial")["implemented"])

    def test_planned_wedding_themes_fail_closed(self):
        for code, theme in WEDDING_PREPRESS_THEMES.items():
            if theme.get("implemented"):
                continue
            with self.assertRaises(PrepressThemeError, msg=code):
                get_prepress_theme(code, require_implemented=True)

    def test_every_wedding_blueprint_has_a_registered_prepress_theme(self):
        wedding = [item for item in COLLECTION_BLUEPRINTS if item["occasion"] == "Weddings"]
        for item in wedding:
            self.assertIn(item["prepress_theme"], WEDDING_PREPRESS_THEMES)

    def test_unknown_theme_is_rejected(self):
        with self.assertRaises(PrepressThemeError):
            get_prepress_theme("not-a-real-theme")


if __name__ == "__main__":
    unittest.main()
