import os
import sys
import unittest

STORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if STORE_DIR not in sys.path:
    sys.path.insert(0, STORE_DIR)

from products import PRODUCTS_BY_SLUG
from prepress.job import SUPPORTED_LANGUAGES
from suite_locales import SUITE_LOCALES
from suite_optional_locales import OPTIONAL_SUITE_LOCALES
from suite_weekend_locales import WEEKEND_SUITE_LOCALES


ACTIVE_LANGUAGES = {"en", "de", "fr", "it", "es", "pt", "nl", "pl", "el", "ru", "tr"}
REMOVED_LANGUAGES = {"uk", "he"}


class ActiveLanguageTests(unittest.TestCase):
    def test_wedding_editor_exposes_only_active_languages(self):
        product = PRODUCTS_BY_SLUG["wedding-day-set"]
        self.assertEqual(set(product["language_presets"]), ACTIVE_LANGUAGES)
        self.assertTrue(REMOVED_LANGUAGES.isdisjoint(product["language_presets"]))

    def test_professional_export_accepts_only_active_languages(self):
        self.assertEqual(SUPPORTED_LANGUAGES, ACTIVE_LANGUAGES)
        self.assertTrue(REMOVED_LANGUAGES.isdisjoint(SUPPORTED_LANGUAGES))

    def test_all_active_languages_have_complete_locale_sources(self):
        for language in ACTIVE_LANGUAGES:
            self.assertIn(language, SUITE_LOCALES)
            self.assertIn(language, OPTIONAL_SUITE_LOCALES)
            self.assertIn(language, WEEKEND_SUITE_LOCALES)


if __name__ == "__main__":
    unittest.main()
