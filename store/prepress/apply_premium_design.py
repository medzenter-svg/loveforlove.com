"""Apply the Love For Love premium decorative layer to generated SLA masters.

Run inside Scribus after base template generation and before CMS/preflight:
  scribus -g -ns -py apply_premium_design.py /path/to/prepress-root

This script changes only design-layer colors and ornaments. Editable text frame
names, text geometry, trim, bleed and safe areas are not modified.
"""

import sys
from pathlib import Path

import scribus


COLOR_IVORY = "LF Ivory"
COLOR_BURGUNDY = "LF Burgundy"
COLOR_GOLD = "LF Gold"
COLOR_INK = "LF Ink"

# CMYK values use Scribus' 0..255 scale. The visual targets are approximately:
# paper #FAF8F3, wine #7A3038, champagne #C0A264, graphite #302B29.
PREMIUM_CMYK = {
    COLOR_IVORY: (0, 2, 7, 5),
    COLOR_BURGUNDY: (0, 155, 138, 133),
    COLOR_GOLD: (0, 40, 122, 63),
    COLOR_INK: (0, 27, 37, 207),
}


def _args():
    args = sys.argv[1:]
    if len(args) != 1:
        raise RuntimeError("Expected: <prepress-root>")
    return Path(args[0]).resolve()


def _set_premium_colors():
    for name, values in PREMIUM_CMYK.items():
        scribus.changeColor(name, *values)


def _refine_border():
    outer = "design__gold_border"
    if not scribus.objectExists(outer):
        raise RuntimeError("Missing design__gold_border")

    scribus.setLineWidth(0.35, outer)
    x, y = scribus.getPosition(outer)
    width, height = scribus.getSize(outer)
    inset = min(width, height) * 0.018

    inner = "design__inner_gold_border"
    if not scribus.objectExists(inner):
        scribus.createRect(
            x + inset,
            y + inset,
            width - (2 * inset),
            height - (2 * inset),
            inner,
        )
    scribus.setFillColor("None", inner)
    scribus.setLineColor(COLOR_GOLD, inner)
    scribus.setLineWidth(0.18, inner)


def _refine_ornament():
    line = "design__ornament"
    if not scribus.objectExists(line):
        return

    scribus.setLineWidth(0.35, line)
    x, y = scribus.getPosition(line)
    width, height = scribus.getSize(line)
    page_width, page_height = scribus.getPageSize()
    dot = min(page_width, page_height) * 0.010
    center_x = x + (width / 2.0)
    center_y = y + (height / 2.0)

    mark = "design__ornament_center"
    if not scribus.objectExists(mark):
        scribus.createEllipse(
            center_x - (dot / 2.0),
            center_y - (dot / 2.0),
            dot,
            dot,
            mark,
        )
    scribus.setFillColor(COLOR_GOLD, mark)
    scribus.setLineColor(COLOR_GOLD, mark)
    scribus.setLineWidth(0.1, mark)


def _apply_one(path):
    scribus.openDoc(str(path))
    try:
        _set_premium_colors()
        _refine_border()
        _refine_ornament()
        scribus.saveDoc()
    finally:
        scribus.closeDoc()


def main():
    root = _args()
    templates = sorted(root.glob("*/*.sla"))
    if len(templates) != 30:
        raise RuntimeError(f"Expected 30 SLA templates, found {len(templates)}")

    for template in templates:
        _apply_one(template)

    print(f"Premium design layer applied to {len(templates)} Scribus templates.")


if __name__ == "__main__":
    main()
