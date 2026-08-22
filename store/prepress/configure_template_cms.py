"""Apply the approved ICC profile names to generated Scribus SLA templates.

This edits only document-level color-management attributes. Run the strict
`check_environment.py --require-profiles` first so the profile names are known
to Scribus on the production worker.
"""

from __future__ import annotations

import argparse
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


REQUIRED_ENV = (
    "LF_RGB_PROFILE_NAME",
    "LF_CMYK_PROFILE_NAME",
    "LF_OUTPUT_PROFILE_NAME",
)


def _profiles_from_env():
    values = {name: os.environ.get(name) for name in REQUIRED_ENV}
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise RuntimeError("Missing CMS environment variables: " + ", ".join(missing))
    return values


def configure_template(path, profiles):
    path = Path(path)
    tree = ET.parse(path)
    root = tree.getroot()
    document = root.find("DOCUMENT")
    if document is None:
        raise RuntimeError(f"SLA DOCUMENT element not found: {path}")

    rgb = profiles["LF_RGB_PROFILE_NAME"]
    cmyk = profiles["LF_CMYK_PROFILE_NAME"]
    output = profiles["LF_OUTPUT_PROFILE_NAME"]

    document.set("HCMS", "1")
    document.set("DPuse", "1")
    document.set("DPPr", output)
    document.set("DPIn", rgb)
    document.set("DPIn2", rgb)
    document.set("DPInCMYK", cmyk)
    document.set("DPIn3", cmyk)
    document.set("DISc", "1")  # relative colorimetric for solid/vector colors
    document.set("DIIm", "0")  # perceptual for raster imagery
    document.set("DPbla", "1")

    tree.write(path, encoding="utf-8", xml_declaration=True)
    return path


def configure_tree(root_dir):
    profiles = _profiles_from_env()
    root_dir = Path(root_dir)
    templates = sorted(root_dir.rglob("*.sla"))
    if not templates:
        raise RuntimeError(f"No SLA templates found under: {root_dir}")

    for template in templates:
        configure_template(template, profiles)
        print(template)
    return len(templates)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root_dir", help="Collection prepress directory or parent containing SLA templates")
    args = parser.parse_args()
    count = configure_tree(args.root_dir)
    print(f"Configured CMS for {count} Scribus templates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
