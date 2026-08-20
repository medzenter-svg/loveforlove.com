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

# CMYK values use Scribus' 0..255 scale. The visual direction is warm white
# paper, deep wine accents, restrained champagne gold and soft graphite text.
PREMIUM_CMYK = {
    COLOR_IVORY: (0, 1, 4, 1),
    COLOR_BURGUNDY: (10, 180, 145, 150),
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


def _line(name, x1, y1, x2, y2, width=0.34):
    if not scribus.objectExists(name):
        scribus.createLine(x1, y1, x2, y2, name)
    scribus.setLineColor(COLOR_GOLD, name)
    scribus.setLineWidth(width, name)


def _dot(name, x, y, diameter):
    if not scribus.objectExists(name):
        scribus.createEllipse(
            x - (diameter / 2.0),
            y - (diameter / 2.0),
            diameter,
            diameter,
            name,
        )
    scribus.setFillColor(COLOR_GOLD, name)
    scribus.setLineColor(COLOR_GOLD, name)
    scribus.setLineWidth(0.08, name)


def _refine_border():
    """Replace the generic full rectangle with restrained editorial corners."""
    outer = "design__gold_border"
    if not scribus.objectExists(outer):
        raise RuntimeError("Missing design__gold_border")

    x, y = scribus.getPosition(outer)
    width, height = scribus.getSize(outer)

    # Hide legacy full/double rectangles. Their geometry remains available as the
    # reference for the premium corner system and therefore does not affect trim.
    scribus.setLineColor("None", outer)
    inner = "design__inner_gold_border"
    if scribus.objectExists(inner):
        scribus.setLineColor("None", inner)

    corner = min(width, height) * 0.105
    right = x + width
    bottom = y + height

    _line("design__corner_tl_h", x, y, x + corner, y)
    _line("design__corner_tl_v", x, y, x, y + corner)
    _line("design__corner_tr_h", right - corner, y, right, y)
    _line("design__corner_tr_v", right, y, right, y + corner)
    _line("design__corner_bl_h", x, bottom, x + corner, bottom)
    _line("design__corner_bl_v", x, bottom - corner, x, bottom)
    _line("design__corner_br_h", right - corner, bottom, right, bottom)
    _line("design__corner_br_v", right, bottom - corner, right, bottom)

    # Tiny center marks make the suite feel intentionally coordinated while
    # remaining minimal enough for destination, floral and formal collections.
    diameter = min(width, height) * 0.0065
    _dot("design__border_top_mark", x + width / 2.0, y, diameter)
    _dot("design__border_bottom_mark", x + width / 2.0, bottom, diameter)


def _refine_ornament():
    """Turn the old single rule into two hairlines with a central gold mark."""
    legacy = "design__ornament"
    if not scribus.objectExists(legacy):
        return

    x, y = scribus.getPosition(legacy)
    width, height = scribus.getSize(legacy)
    center_x = x + (width / 2.0)
    center_y = y + (height / 2.0)
    gap = width * 0.12

    scribus.setLineColor("None", legacy)
    _line(
        "design__ornament_left",
        x,
        center_y,
        center_x - (gap / 2.0),
        center_y,
        width=0.28,
    )
    _line(
        "design__ornament_right",
        center_x + (gap / 2.0),
        center_y,
        x + width,
        center_y,
        width=0.28,
    )

    page_width, page_height = scribus.getPageSize()
    diameter = min(page_width, page_height) * 0.008
    _dot("design__ornament_center", center_x, center_y, diameter)


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
