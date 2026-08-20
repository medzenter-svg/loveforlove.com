import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

STORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if STORE_DIR not in sys.path:
    sys.path.insert(0, STORE_DIR)

from prepress.configure_template_cms import configure_template
from prepress.template_preflight import TemplatePreflightError, validate_template


MM_TO_PT = 72.0 / 25.4


class TemplatePreflightTests(unittest.TestCase):
    ENV = {
        "LF_RGB_PROFILE_NAME": "sRGB Test",
        "LF_CMYK_PROFILE_NAME": "eciCMYK Test",
        "LF_OUTPUT_PROFILE_NAME": "eciCMYK Test",
    }

    def _write_invitation_sla(self, directory, bleed_mm=3, cms=False):
        path = Path(directory) / "invitation.sla"
        bleed_pt = bleed_mm * MM_TO_PT
        cms_attrs = (
            'HCMS="1" DPuse="1" DPPr="eciCMYK Test" DPIn="sRGB Test" '
            'DPIn2="sRGB Test" DPInCMYK="eciCMYK Test" DPIn3="eciCMYK Test"'
            if cms else
            'HCMS="0" DPuse="0" DPPr="" DPIn="" DPIn2="" DPInCMYK="" DPIn3=""'
        )
        path.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<SCRIBUSUTF8NEW Version="1.6.1">\n'
            f'<DOCUMENT PAGEWIDTH="{105 * MM_TO_PT}" PAGEHEIGHT="{148 * MM_TO_PT}" '
            f'BleedTop="{bleed_pt}" BleedLeft="{bleed_pt}" '
            f'BleedRight="{bleed_pt}" BleedBottom="{bleed_pt}" {cms_attrs}/>'
            '\n</SCRIBUSUTF8NEW>\n',
            encoding="utf-8",
        )
        return path

    def test_template_passes_after_cms_configuration(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, self.ENV, clear=False):
            path = self._write_invitation_sla(tmp, cms=False)
            configure_template(path, self.ENV)
            self.assertTrue(validate_template(path, "international_metric", "invitation"))

    def test_cms_disabled_template_fails(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, self.ENV, clear=False):
            path = self._write_invitation_sla(tmp, cms=False)
            with self.assertRaises(TemplatePreflightError):
                validate_template(path, "international_metric", "invitation")

    def test_insufficient_bleed_fails(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, self.ENV, clear=False):
            path = self._write_invitation_sla(tmp, bleed_mm=1, cms=True)
            with self.assertRaises(TemplatePreflightError):
                validate_template(path, "international_metric", "invitation")

    def test_wrong_output_profile_fails(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, self.ENV, clear=False):
            path = self._write_invitation_sla(tmp, cms=True)
            path.write_text(
                path.read_text(encoding="utf-8").replace('DPPr="eciCMYK Test"', 'DPPr="Wrong Profile"'),
                encoding="utf-8",
            )
            with self.assertRaises(TemplatePreflightError):
                validate_template(path, "international_metric", "invitation")


if __name__ == "__main__":
    unittest.main()
