"""Run inside Scribus to verify premium fonts on generated SLA templates.

Usage:
  scribus -g -ns -py check_template_fonts.py /path/to/prepress-root
"""

import os
import sys
from pathlib import Path

import scribus


TITLE_FONT = os.environ.get("LF_TITLE_FONT", "EB Garamond 12 Regular")
BODY_FONT = os.environ.get("LF_BODY_FONT", "Lato Regular")
ALLOWED_FONTS = {TITLE_FONT, BODY_FONT}


def _args():
    args = sys.argv[1:]
    if len(args) != 1:
        raise RuntimeError("Expected: <prepress-root>")
    return Path(args[0]).resolve()


def _verify_font_inventory():
    available = set(scribus.getFontNames())
    missing = sorted(ALLOWED_FONTS - available)
    if missing:
        raise RuntimeError(
            "Required premium fonts are not visible to Scribus: " + ", ".join(missing)
        )


def _verify_template(path):
    scribus.openDoc(str(path))
    try:
        checked = 0
        failures = []
        for item in scribus.getAllObjects():
            if not (item.startswith("txt__") or item.startswith("lbl__")):
                continue
            checked += 1
            font_name = scribus.getFont(item)
            if font_name not in ALLOWED_FONTS:
                failures.append(f"{item}={font_name}")
        if checked == 0:
            raise RuntimeError(f"No editable text frames found in {path}")
        if failures:
            raise RuntimeError(
                f"Template uses fallback/unapproved fonts: {path}: " + "; ".join(failures)
            )
        return checked
    finally:
        scribus.closeDoc()


def main():
    root = _args()
    if not root.is_dir():
        raise RuntimeError(f"Prepress template root not found: {root}")

    _verify_font_inventory()
    templates = sorted(root.glob("*/*.sla"))
    if len(templates) != 30:
        raise RuntimeError(f"Expected 30 SLA templates, found {len(templates)}")

    frames = 0
    for template in templates:
        frames += _verify_template(template)

    print(
        f"Premium font check passed: {len(templates)} templates, {frames} editable frames, "
        f"fonts={sorted(ALLOWED_FONTS)}"
    )


if __name__ == "__main__":
    main()
