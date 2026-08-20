"""Apply one explicitly approved Love For Love visual theme to SLA masters.

Run inside Scribus after base template generation and before CMS/preflight:
  scribus -g -ns -py apply_premium_design.py /path/to/prepress-root [theme-code]

Only implemented themes may export. Planned catalog collections fail closed until
their own print design has been built and QA'd.
"""

import os
import sys
from pathlib import Path

import scribus

STORE_DIR = Path(__file__).resolve().parents[1]
if str(STORE_DIR) not in sys.path:
    sys.path.insert(0, str(STORE_DIR))

from prepress.design_themes import DEFAULT_PREPRESS_THEME, get_prepress_theme


COLOR_IVORY = "LF Ivory"
COLOR_BURGUNDY = "LF Burgundy"
COLOR_GOLD = "LF Gold"
COLOR_INK = "LF Ink"


def _args():
    args = sys.argv[1:]
    if len(args) not in (1, 2):
        raise RuntimeError("Expected: <prepress-root> [theme-code]")
    root = Path(args[0]).resolve()
    theme_code = args[1] if len(args) == 2 else os.environ.get("LF_DESIGN_THEME", DEFAULT_PREPRESS_THEME)
    return root, str(theme_code)


def _set_theme_colors(theme):
    mapping = {
        COLOR_IVORY: theme["paper"],
        COLOR_BURGUNDY: theme["accent"],
        COLOR_GOLD: theme["gold"],
        COLOR_INK: theme["ink"],
    }
    for name, values in mapping.items():
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


def _open_corner_border():
    outer = "design__gold_border"
    if not scribus.objectExists(outer):
        raise RuntimeError("Missing design__gold_border")

    x, y = scribus.getPosition(outer)
    width, height = scribus.getSize(outer)
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

    diameter = min(width, height) * 0.0065
    _dot("design__border_top_mark", x + width / 2.0, y, diameter)
    _dot("design__border_bottom_mark", x + width / 2.0, bottom, diameter)


def _paired_rule_ornament():
    legacy = "design__ornament"
    if not scribus.objectExists(legacy):
        return

    x, y = scribus.getPosition(legacy)
    width, height = scribus.getSize(legacy)
    center_x = x + (width / 2.0)
    center_y = y + (height / 2.0)
    gap = width * 0.12

    scribus.setLineColor("None", legacy)
    _line("design__ornament_left", x, center_y, center_x - gap / 2.0, center_y, width=0.28)
    _line("design__ornament_right", center_x + gap / 2.0, center_y, x + width, center_y, width=0.28)

    page_width, page_height = scribus.getPageSize()
    _dot(
        "design__ornament_center",
        center_x,
        center_y,
        min(page_width, page_height) * 0.008,
    )


def _apply_motif(theme):
    motif = theme.get("motif")
    if motif == "open_corners":
        _open_corner_border()
        _paired_rule_ornament()
        return
    raise RuntimeError(f"Theme motif is not implemented in Scribus: {motif}")


def _apply_one(path, theme):
    scribus.openDoc(str(path))
    try:
        _set_theme_colors(theme)
        _apply_motif(theme)
        scribus.saveDoc()
    finally:
        scribus.closeDoc()


def main():
    root, theme_code = _args()
    theme = get_prepress_theme(theme_code, require_implemented=True)
    templates = sorted(root.glob("*/*.sla"))
    if len(templates) != 30:
        raise RuntimeError(f"Expected 30 SLA templates, found {len(templates)}")

    for template in templates:
        _apply_one(template, theme)

    print(
        f"Premium design theme '{theme_code}' applied to {len(templates)} Scribus templates."
    )


if __name__ == "__main__":
    main()
