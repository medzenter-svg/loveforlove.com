"""Apply an approved or isolated prototype Love For Love visual theme to SLA masters.

Production usage:
  scribus -g -ns -py apply_premium_design.py /path/to/prepress-root [theme-code]

Prototype usage (never unlocks full-package export or sale):
  scribus -g -ns -py apply_premium_design.py /path/to/prepress-root theme-code --prototype --piece=invitation
"""

import math
import os
import sys
from pathlib import Path

import scribus

STORE_DIR = Path(__file__).resolve().parents[1]
if str(STORE_DIR) not in sys.path:
    sys.path.insert(0, str(STORE_DIR))

from prepress.design_themes import DEFAULT_PREPRESS_THEME, get_prepress_theme, get_prototype_theme

COLOR_IVORY = "LF Ivory"
COLOR_BURGUNDY = "LF Burgundy"
COLOR_GOLD = "LF Gold"
COLOR_INK = "LF Ink"
COLOR_SECONDARY = "LF Secondary"
COLOR_TERTIARY = "LF Tertiary"
PROTOTYPE_MARKER_PREFIX = ".loveforlove-prototype-"


def _args():
    args = sys.argv[1:]
    if not args:
        raise RuntimeError("Expected: <prepress-root> [theme-code] [--prototype] [--piece=invitation]")
    root = Path(args[0]).resolve()
    theme_code = DEFAULT_PREPRESS_THEME
    prototype = False
    piece = None
    for token in args[1:]:
        if token == "--prototype":
            prototype = True
        elif token.startswith("--piece="):
            piece = token.split("=", 1)[1].strip()
        elif not token.startswith("--"):
            theme_code = token
        else:
            raise RuntimeError(f"Unknown design option: {token}")
    return root, str(theme_code), prototype, piece


def _ensure_color(name, values):
    if values is None:
        return False
    try:
        scribus.changeColor(name, *values)
    except Exception:
        scribus.defineColor(name, *values)
    return True


def _set_theme_colors(theme):
    _ensure_color(COLOR_IVORY, theme["paper"])
    _ensure_color(COLOR_BURGUNDY, theme["accent"])
    _ensure_color(COLOR_GOLD, theme["gold"])
    _ensure_color(COLOR_INK, theme["ink"])
    _ensure_color(COLOR_SECONDARY, theme.get("secondary"))
    _ensure_color(COLOR_TERTIARY, theme.get("tertiary"))


def _line(name, x1, y1, x2, y2, width=0.34, color=COLOR_GOLD):
    if not scribus.objectExists(name):
        scribus.createLine(x1, y1, x2, y2, name)
    scribus.setLineColor(color, name)
    scribus.setLineWidth(width, name)


def _polyline(name, points, color=COLOR_GOLD, width=0.30):
    if not scribus.objectExists(name):
        scribus.createPolyLine(points, name)
    scribus.setLineColor(color, name)
    scribus.setLineWidth(width, name)
    try:
        scribus.setFillColor("None", name)
    except Exception:
        pass


def _dot(name, x, y, diameter, color=COLOR_GOLD):
    if not scribus.objectExists(name):
        scribus.createEllipse(x - diameter / 2.0, y - diameter / 2.0, diameter, diameter, name)
    scribus.setFillColor(color, name)
    scribus.setLineColor(color, name)
    scribus.setLineWidth(0.08, name)


def _oval(name, x, y, width, height, color):
    if not scribus.objectExists(name):
        scribus.createEllipse(x - width / 2.0, y - height / 2.0, width, height, name)
    scribus.setFillColor(color, name)
    scribus.setLineColor(color, name)
    scribus.setLineWidth(0.05, name)


def _rect(name, x, y, width, height, color):
    if not scribus.objectExists(name):
        scribus.createRect(x, y, width, height, name)
    scribus.setFillColor(color, name)
    scribus.setLineColor(color, name)
    scribus.setLineWidth(0.01, name)


def _diamond(name, cx, cy, half_w, half_h, color, width=0.28):
    points = [cx, cy - half_h, cx + half_w, cy, cx, cy + half_h, cx - half_w, cy, cx, cy - half_h]
    _polyline(name, points, color, width)


def _hide_legacy_frame():
    for name in (
        "design__gold_border", "design__inner_gold_border", "design__ornament",
        "design__ornament_left", "design__ornament_right", "design__ornament_center",
    ):
        if scribus.objectExists(name):
            try:
                scribus.setLineColor("None", name)
            except Exception:
                pass
            try:
                scribus.setFillColor("None", name)
            except Exception:
                pass


def _page_geometry():
    width, height = scribus.getPageSize()
    inset = min(width, height) * 0.045
    return width, height, inset


def _open_corner_border():
    outer = "design__gold_border"
    if not scribus.objectExists(outer):
        raise RuntimeError("Missing design__gold_border")
    x, y = scribus.getPosition(outer)
    width, height = scribus.getSize(outer)
    _hide_legacy_frame()
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
    center_x = x + width / 2.0
    center_y = y + height / 2.0
    gap = width * 0.12
    scribus.setLineColor("None", legacy)
    _line("design__ornament_left", x, center_y, center_x - gap / 2.0, center_y, width=0.28)
    _line("design__ornament_right", center_x + gap / 2.0, center_y, x + width, center_y, width=0.28)
    page_width, page_height = scribus.getPageSize()
    _dot("design__ornament_center", center_x, center_y, min(page_width, page_height) * 0.008)


def _arch_points(left, right, shoulder_y, apex_y, samples=35):
    center_x = (left + right) / 2.0
    radius_x = (right - left) / 2.0
    radius_y = shoulder_y - apex_y
    points = []
    for index in range(samples):
        fraction = index / float(samples - 1)
        angle = math.pi * (1.0 - fraction)
        points.extend([center_x + radius_x * math.cos(angle), shoulder_y - radius_y * math.sin(angle)])
    return points


def _wave_points(left, right, center_y, amplitude, cycles=2.2, samples=41):
    points = []
    for index in range(samples):
        fraction = index / float(samples - 1)
        x = left + (right - left) * fraction
        y = center_y + math.sin(fraction * cycles * math.pi * 2.0) * amplitude
        points.extend([x, y])
    return points


def _amalfi_arch():
    _hide_legacy_frame()
    width, height, inset = _page_geometry()
    left = inset * 1.20
    right = width - inset * 1.20
    shoulder_y = height * 0.285
    apex_y = height * 0.055
    base_y = height * 0.865
    _line("design__amalfi_left", left, shoulder_y, left, base_y, width=0.30)
    _line("design__amalfi_right", right, shoulder_y, right, base_y, width=0.30)
    _polyline("design__amalfi_arch", _arch_points(left, right, shoulder_y, apex_y), COLOR_GOLD, 0.30)
    inner_left = inset * 1.85
    inner_right = width - inset * 1.85
    _line("design__amalfi_olive_left", inner_left, height * 0.325, inner_left, height * 0.805, width=0.18, color=COLOR_SECONDARY)
    _line("design__amalfi_olive_right", inner_right, height * 0.325, inner_right, height * 0.805, width=0.18, color=COLOR_SECONDARY)
    center_x = width / 2.0
    coral_y = height * 0.11
    _dot("design__amalfi_coral_mark", center_x, coral_y, min(width, height) * 0.009, COLOR_TERTIARY)
    _line("design__amalfi_coral_rule_left", center_x - width * 0.055, coral_y, center_x - width * 0.016, coral_y, width=0.22, color=COLOR_TERTIARY)
    _line("design__amalfi_coral_rule_right", center_x + width * 0.016, coral_y, center_x + width * 0.055, coral_y, width=0.22, color=COLOR_TERTIARY)
    _line("design__amalfi_baseline", width * 0.33, height * 0.91, width * 0.67, height * 0.91, width=0.24)


def _monaco_regatta():
    _hide_legacy_frame()
    width, height, inset = _page_geometry()
    mast_x = inset * 1.15
    _line("design__monaco_mast", mast_x, height * 0.065, mast_x, height * 0.935, width=0.92, color=COLOR_BURGUNDY)
    _line("design__monaco_top", mast_x, height * 0.065, width * 0.64, height * 0.065, width=0.55, color=COLOR_BURGUNDY)
    _line("design__monaco_diagonal", width * 0.64, height * 0.065, width * 0.72, height * 0.12, width=0.42, color=COLOR_BURGUNDY)
    _rect("design__monaco_signal", width * 0.75, height * 0.057, width * 0.14, max(height * 0.006, 0.7), COLOR_SECONDARY)
    _line("design__monaco_bottom", width * 0.58, height * 0.915, width - inset, height * 0.915, width=0.45, color=COLOR_GOLD)
    _dot("design__monaco_gold_dot", width * 0.55, height * 0.915, min(width, height) * 0.009, COLOR_GOLD)
    _paired_rule_ornament()


def _como_lake_line():
    _hide_legacy_frame()
    width, height, inset = _page_geometry()
    y = height * 0.875
    _polyline("design__como_water_1", _wave_points(inset, width * 0.56, y, height * 0.0042), COLOR_BURGUNDY, 0.44)
    _polyline("design__como_water_2", _wave_points(width * 0.24, width - inset, y + height * 0.020, height * 0.0034), COLOR_BURGUNDY, 0.30)
    _line("design__como_water_3", inset, y + height * 0.042, width * 0.70, y + height * 0.042, width=0.24, color=COLOR_GOLD)
    _dot("design__como_sage", width * 0.77, y + height * 0.042, min(width, height) * 0.012, COLOR_SECONDARY)
    _line("design__como_top", width * 0.36, height * 0.072, width * 0.64, height * 0.072, width=0.30, color=COLOR_GOLD)
    _dot("design__como_top_mark", width / 2.0, height * 0.072, min(width, height) * 0.008, COLOR_SECONDARY)
    _paired_rule_ornament()


def _provence_botanical():
    _hide_legacy_frame()
    width, height, inset = _page_geometry()
    # Sparse upper-right botanical punctuation; never a full floral border.
    _line("design__provence_stem_top", width * 0.865, height * 0.055, width * 0.935, height * 0.185, width=0.24, color=COLOR_GOLD)
    _oval("design__provence_leaf_1", width * 0.885, height * 0.095, width * 0.038, height * 0.018, COLOR_SECONDARY)
    _oval("design__provence_leaf_2", width * 0.913, height * 0.138, width * 0.032, height * 0.016, COLOR_BURGUNDY)
    _dot("design__provence_bud", width * 0.936, height * 0.181, min(width, height) * 0.010, COLOR_TERTIARY)
    # Small mirrored lower-left mark for balance.
    _line("design__provence_stem_bottom", width * 0.075, height * 0.865, width * 0.135, height * 0.925, width=0.22, color=COLOR_GOLD)
    _oval("design__provence_leaf_3", width * 0.098, height * 0.888, width * 0.030, height * 0.015, COLOR_BURGUNDY)
    _dot("design__provence_bud_bottom", width * 0.073, height * 0.863, min(width, height) * 0.008, COLOR_SECONDARY)
    _line("design__provence_top_rule", width * 0.39, height * 0.065, width * 0.61, height * 0.065, width=0.24, color=COLOR_GOLD)
    _paired_rule_ornament()


def _santorini_arch_sun():
    _hide_legacy_frame()
    width, height, inset = _page_geometry()
    left = width * 0.36
    right = width * 0.64
    shoulder = height * 0.105
    apex = height * 0.035
    _polyline("design__santorini_arch", _arch_points(left, right, shoulder, apex, samples=29), COLOR_BURGUNDY, 0.56)
    _line("design__santorini_left", left, shoulder, left, height * 0.135, width=0.56, color=COLOR_BURGUNDY)
    _line("design__santorini_right", right, shoulder, right, height * 0.135, width=0.56, color=COLOR_BURGUNDY)
    _dot("design__santorini_sun", width / 2.0, height * 0.078, min(width, height) * 0.021, COLOR_TERTIARY)
    _line("design__santorini_horizon", inset, height * 0.905, width - inset, height * 0.905, width=0.34, color=COLOR_BURGUNDY)
    _line("design__santorini_gold_horizon", width * 0.37, height * 0.923, width * 0.63, height * 0.923, width=0.22, color=COLOR_GOLD)
    _paired_rule_ornament()


def _flower(prefix, cx, cy, scale, petal_color, center_color):
    petal_w = scale * 0.80
    petal_h = scale * 0.48
    radius = scale * 0.54
    positions = [(0, -radius), (radius, 0), (0, radius), (-radius, 0)]
    for index, (dx, dy) in enumerate(positions, 1):
        _oval(f"{prefix}_petal_{index}", cx + dx, cy + dy, petal_w, petal_h, petal_color)
    _dot(f"{prefix}_center", cx, cy, scale * 0.34, center_color)


def _riviera_floral():
    _hide_legacy_frame()
    width, height, inset = _page_geometry()
    scale = min(width, height) * 0.050
    # Fashion-editorial, asymmetric floral punctuation rather than a frame.
    _line("design__riviera_stem_top", width * 0.885, height * 0.045, width * 0.835, height * 0.205, width=0.34, color=COLOR_SECONDARY)
    _flower("design__riviera_top", width * 0.875, height * 0.105, scale, COLOR_BURGUNDY, COLOR_GOLD)
    _oval("design__riviera_leaf_top", width * 0.846, height * 0.174, scale * 0.75, scale * 0.34, COLOR_SECONDARY)
    _line("design__riviera_stem_bottom", width * 0.105, height * 0.805, width * 0.075, height * 0.945, width=0.30, color=COLOR_SECONDARY)
    _flower("design__riviera_bottom", width * 0.105, height * 0.875, scale * 0.75, COLOR_TERTIARY, COLOR_GOLD)
    _line("design__riviera_gold_rule", width * 0.36, height * 0.925, width * 0.64, height * 0.925, width=0.24, color=COLOR_GOLD)
    _paired_rule_ornament()


def _vienna_crest():
    _hide_legacy_frame()
    width, height, inset = _page_geometry()
    cx = width / 2.0
    cy = height * 0.072
    _diamond("design__vienna_crest_outer", cx, cy, width * 0.060, height * 0.034, COLOR_GOLD, 0.32)
    _diamond("design__vienna_crest_inner", cx, cy, width * 0.034, height * 0.019, COLOR_SECONDARY, 0.22)
    _dot("design__vienna_crest_mark", cx, cy, min(width, height) * 0.008, COLOR_BURGUNDY)
    _line("design__vienna_axis_top", cx, height * 0.025, cx, cy - height * 0.036, width=0.20, color=COLOR_GOLD)
    _line("design__vienna_axis_bottom", cx, cy + height * 0.036, cx, height * 0.135, width=0.20, color=COLOR_GOLD)
    _line("design__vienna_lower_1", width * 0.31, height * 0.905, width * 0.69, height * 0.905, width=0.24, color=COLOR_GOLD)
    _line("design__vienna_lower_2", width * 0.38, height * 0.918, width * 0.62, height * 0.918, width=0.18, color=COLOR_SECONDARY)
    _paired_rule_ornament()


def _apply_motif(theme):
    motif = theme.get("motif")
    if motif == "open_corners":
        _open_corner_border(); _paired_rule_ornament()
    elif motif == "amalfi_arch":
        _amalfi_arch()
    elif motif == "regatta_rules":
        _monaco_regatta()
    elif motif == "lake_line":
        _como_lake_line()
    elif motif == "botanical_punctuation":
        _provence_botanical()
    elif motif == "aegean_arch_sun":
        _santorini_arch_sun()
    elif motif == "asymmetric_floral":
        _riviera_floral()
    elif motif == "ceremonial_crest":
        _vienna_crest()
    else:
        raise RuntimeError(f"Theme motif is not implemented in Scribus: {motif}")


def _apply_one(path, theme):
    scribus.openDoc(str(path))
    try:
        _set_theme_colors(theme)
        _apply_motif(theme)
        scribus.saveDoc()
    finally:
        scribus.closeDoc()


def _prototype_marker(root, theme_code):
    return root / f"{PROTOTYPE_MARKER_PREFIX}{theme_code}"


def main():
    root, theme_code, prototype, piece = _args()
    marker = _prototype_marker(root, theme_code)
    if marker.exists():
        marker.unlink()
    if prototype:
        if not piece:
            raise RuntimeError("Prototype mode requires --piece=<piece>")
        theme = get_prototype_theme(theme_code, piece)
        templates = sorted(root.glob(f"*/{piece}.sla"))
        if len(templates) != 2:
            raise RuntimeError(f"Expected 2 prototype SLA templates for {piece}, found {len(templates)}")
    else:
        theme = get_prepress_theme(theme_code, require_implemented=True)
        templates = sorted(root.glob("*/*.sla"))
        if len(templates) != 30:
            raise RuntimeError(f"Expected 30 SLA templates, found {len(templates)}")
    for template in templates:
        _apply_one(template, theme)
    if prototype:
        marker.write_text(
            f"theme={theme_code}\npiece={piece}\ntemplates={len(templates)}\nmotif={theme.get('motif')}\n",
            encoding="utf-8",
        )
    mode = "prototype" if prototype else "production"
    print(f"Theme '{theme_code}' applied to {len(templates)} Scribus templates in {mode} mode.")


if __name__ == "__main__":
    main()
