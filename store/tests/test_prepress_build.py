import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

STORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if STORE_DIR not in sys.path:
    sys.path.insert(0, STORE_DIR)

from prepress import build_package


class PrepressBuildTests(unittest.TestCase):
    def test_scribus_python_script_is_last_scribus_option(self):
        with mock.patch("prepress.build_package.shutil.which", return_value=None):
            command = build_package._scribus_command(
                "scribus",
                Path("template.sla"),
                Path("output.pdf"),
                Path("job.json"),
                "pdfx4_worldwide",
            )
        py_index = command.index("-py")
        self.assertEqual(command[py_index + 1], str(build_package.SCRIBUS_EXPORT_SCRIPT))
        self.assertEqual(
            command[py_index + 2:],
            ["template.sla", "output.pdf", "job.json", "pdfx4_worldwide"],
        )
        self.assertNotIn("--", command)

    def test_load_job_rejects_unknown_fields_before_scribus(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "job.json"
            path.write_text(json.dumps({
                "collection_slug": "wedding-day-set",
                "fields": {"unexpected": "value"},
                "labels": {},
            }), encoding="utf-8")
            with self.assertRaises(RuntimeError):
                build_package._load_job(path)

    def test_load_job_returns_normalized_customer_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "job.json"
            path.write_text(json.dumps({
                "collection_slug": "wedding-day-set",
                "language": "fr",
                "enabled_optional": ["program_day_1", "program_day_1"],
                "fields": {"venueAddress": "A\r\nB"},
                "labels": {"day_one": "Jour 1"},
            }), encoding="utf-8")
            job = build_package._load_job(path)
            self.assertEqual(job["language"], "fr")
            self.assertEqual(job["enabled_optional"], ["program_day_1"])
            self.assertEqual(job["fields"]["venueAddress"], "A\nB")


if __name__ == "__main__":
    unittest.main()
