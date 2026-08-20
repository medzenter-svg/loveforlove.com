"""Apply the gated Amalfi Luce visual prototype to Invitation SLA masters only.

This script is intentionally NOT a production theme exporter. It accepts only the
Amalfi Invitation prototype and keeps the collection's full-package release gate
closed until the design is approved and implemented across all 15 pieces.
"""

import sys
from pathlib import Path

import scribus

STORE_DIR = Path(__file__).resolve().parents[1]
if str(STORE_DIR) not in sys.path:
    sys.path.insert(0, str(STORE_DIR))

from prepress.design_themes import get_prototype_theme


THEME_CODE = "amalfi-luce"
PIECE = "invitation"
COLOR_PAPER = "LF Ivory"
COLOR_ACCENT = "LF Burgundy"
COLOR_GOLD = "LF Gold"
COLOR_INK = "LF Ink"
COLOR_OLIVE = "LF Amalfi Olive"
COLOR_CORAL = "LF Amalfi Coral"


def _args():
    args = sys.argv[1:]
    if len(args) != 1:
        raise RuntimeError("Expected: <prepress-root>")
    return Path(args[0]).resolve()


def _define_theme_colors(theme):
    scribus.changeColor(COLOR_PAPER, *theme["paper"])
    scribus.changeColor(COLOR_ACCENT, *theme["accent"])
    scribus.changeColor(COLOR_GOLD, *theme["gold"])
    scribus.changeColor(COLOR_INK, *theme["ink"])
    scribus.defineColor(COLOR_OLIVE, *theme["secondary"])
    scribus.defineColor(COLOR_CORAL, *theme["accent"])


def _hide_base_ornaments():
    for name in (
        "design__gold_border",
        "design__inner_gold_border",
        "design__ornament",
        "design__ornament_left",
        "design__ornament_right",
        "design__ornament_center",
    ):
        if not scribus.objectExists(name):
            continue
        try:
            scribus.setLineColor("None", name)
        except Exception:
            pass
        try:
            scribus.setFillColor("None", name)
        except Exception:
            pass


def _line(name, x1, y1, x2, y2, color, width):
    if not scribus.objectExists(name):
        scribus.createLine(x1, y1, x2, y2, name)
    scribus.setLineColor(color, name)
    scribus.setLineWidth(width, name)


def _curve(name, points, color, width):
    if not scribus.objectExists(name):
        scribus.createBezierLine(points, name)
    scribus.setLineColor(color, name)
    scribus.setLineWidth(width, name)
    try:
        scribus.setFillColor("None", name)
    except Exception:
        pass


def _dot(name, x, y, diameter, color):
    if not scribus.objectExists(name):
        scribus.createEllipse(x - diameter / 2.0, y - diameter / 2.0, diameter, diameter, name)
    scribus.setFillColor(color, name)
    scribus.setLineColor(color, name)
    scribus.setLineWidth(0.05, name)


def _portal_geometry():
    border = "design__gold_border"
    if not scribus.objectExists(border):
        raise RuntimeError("Invitation template is missing design__gold_border")

    x, y = scribus.getPosition(border)
    width, height = scribus.getSize(border)
    left = x + width * 0.055
    right = x + width * 0.945
    shoulder_y = y + height * 0.265
    base_y = y + height * 0.865
    apex_y = y + height * 0.055
    control_y = y + height * 0.075

    # Tall gold doorway/terrace geometry: the curved top is deliberately open and
    # architectural, not a floral frame or literal postcard illustration.
    _line("design__amalfi_left", left, shoulder_y, left, base_y, COLOR_GOLD, 0.30)
    _line("design__amalfi_right", right, shoulder_y, right, base_y, COLOR_GOLD, 0.30)
    _curve(
        "design__amalfi_arch",
        [
            left, shoulder_y, left + width * 0.06, control_y,
            right, shoulder_y, right - width * 0.06, control_y,
        ],
        COLOR_GOLD,
        0.30,
    )

    # A second, shorter olive line gives the collection its own Mediterranean
    # identity without turning the invitation into an illustrated travel card.
    inner_left = x + width * 0.085
    inner_right = x + width * 0.915
    inner_shoulder = y + height * 0.305
    inner_base = y + height * 0.805
    _line("design__amalfi_olive_left", inner_left, inner_shoulder, inner_left, inner_base, COLOR_OLIVE, 0.18)
    _line("design__amalfi_olive_right", inner_right, inner_shoulder, inner_right, inner_base, COLOR_OLIVE, 0.18)

    # Small coral sun/flower punctuation above the names; abstract enough to remain
    # elegant across formal destination weddings.
    center_x = x + width / 2.0
    coral_y = y + height * 0.105
    diameter = min(width, height) * 0.009
    _dot("design__amalfi_coral_mark", center_x, coral_y, diameter, COLOR_CORAL)
    _line(
        "design__amalfi_coral_rule_left",
        center_x - width * 0.055,
        coral_y,
        center_x - width * 0.016,
        coral_y,
        COLOR_CORAL,
        0.22,
    )
    _line(
        "design__amalfi_coral_rule_right",
        center_x + width * 0.016,
        coral_y,
        center_x + width * 0.055,
        coral_y,
        COLOR_CORAL,
        0.22,
    )

    # Fine gold baseline anchors the portal without enclosing the page.
    _line(
        "design__amalfi_baseline",
        x + width * 0.33,
        y + height * 0.905,
        x + width * 0.67,
        y + height * 0.905,
        COLOR_GOLD,
        0.24,
    )


def _apply_one(path, theme):
    scribus.openDoc(str(path))
    try:
        _define_theme_colors(theme)
        _hide_base_ornaments()
        _portal_geometry()
        scribus.saveDoc()
    finally:
        scribus.closeDoc()


def main():
    root = _args()
    theme = get_prototype_theme(THEME_CODE, PIECE)
    invitations = sorted(root.glob(f"*/{PIECE}.sla"))
    if len(invitations) != 2:
        raise RuntimeError(f"Expected two Invitation SLA templates, found {len(invitations)}")

    for template in invitations:
        _apply_one(template, theme)

    print(f"Amalfi Luce Invitation prototype applied to {len(invitations)} templates.")


if __name__ == "__main__":
    main()
