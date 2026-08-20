"""Second-pass visual refinement for selected Invitation prototypes only.

This file deliberately sits outside the stable production theme renderer. It can
be removed without touching Paris Editorial or the four prototype directions that
already passed visual review. Supported refinements:
- monaco-regatta: replace corporate corner geometry with an abstract couture sail
- provence-rose: replace tiny punctuation with airy line-art botanical branches
- riviera-garden: replace filled icon flowers with editorial outline florals

Run inside Scribus after apply_premium_design.py:
  scribus -g -ns -py refine_invitation_prototypes.py PREPRESS_ROOT THEME
"""

import math
import sys
from pathlib import Path

import scribus


SUPPORTED = {"monaco-regatta", "provence-rose", "riviera-garden"}
COLOR_ACCENT = "LF Burgundy"
COLOR_GOLD = "LF Gold"
COLOR_SECONDARY = "LF Secondary"
COLOR_TERTIARY = "LF Tertiary"
MARKER_PREFIX = ".loveforlove-refined-"


def _args():
    args = sys.argv[1:]
    if len(args) != 2:
        raise RuntimeError("Expected: <prepress-root> <theme-code>")
    root = Path(args[0]).resolve()
    theme = str(args[1]).strip()
    if theme not in SUPPORTED:
        raise RuntimeError(f"Unsupported refinement theme: {theme}")
    return root, theme


def _hide(name):
    if not scribus.objectExists(name):
        return
    try:
        scribus.setLineColor("None", name)
    except Exception:
        pass
    try:
        scribus.setFillColor("None", name)
    except Exception:
        pass


def _line(name, x1, y1, x2, y2, color, width=0.28):
    if not scribus.objectExists(name):
        scribus.createLine(x1, y1, x2, y2, name)
    scribus.setLineColor(color, name)
    scribus.setLineWidth(width, name)


def _polyline(name, points, color, width=0.25):
    if not scribus.objectExists(name):
        scribus.createPolyLine(points, name)
    scribus.setLineColor(color, name)
    scribus.setLineWidth(width, name)
    try:
        scribus.setFillColor("None", name)
    except Exception:
        pass


def _dot(name, cx, cy, diameter, color, filled=True, width=0.18):
    if not scribus.objectExists(name):
        scribus.createEllipse(cx - diameter / 2.0, cy - diameter / 2.0, diameter, diameter, name)
    scribus.setLineColor(color, name)
    scribus.setLineWidth(width, name)
    scribus.setFillColor(color if filled else "None", name)


def _quadratic_points(p0, p1, p2, samples=25):
    points = []
    for index in range(samples):
        t = index / float(samples - 1)
        u = 1.0 - t
        x = u * u * p0[0] + 2.0 * u * t * p1[0] + t * t * p2[0]
        y = u * u * p0[1] + 2.0 * u * t * p1[1] + t * t * p2[1]
        points.extend([x, y])
    return points


def _lens_points(cx, cy, length, width, angle_degrees, samples=13):
    angle = math.radians(angle_degrees)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    local = []
    for index in range(samples):
        t = index / float(samples - 1)
        x = -length / 2.0 + length * t
        y = (width / 2.0) * math.sin(math.pi * t)
        local.append((x, y))
    for index in range(samples - 1, -1, -1):
        t = index / float(samples - 1)
        x = -length / 2.0 + length * t
        y = -(width / 2.0) * math.sin(math.pi * t)
        local.append((x, y))
    local.append(local[0])

    points = []
    for x, y in local:
        rx = cx + x * cos_a - y * sin_a
        ry = cy + x * sin_a + y * cos_a
        points.extend([rx, ry])
    return points


def _leaf(name, cx, cy, length, width, angle, color, line_width=0.20):
    _polyline(name, _lens_points(cx, cy, length, width, angle), color, line_width)


def _outlined_flower(prefix, cx, cy, scale, petal_color, center_color, petal_count=5):
    radius = scale * 0.58
    for index in range(petal_count):
        angle = -90.0 + (360.0 / petal_count) * index
        radians = math.radians(angle)
        px = cx + math.cos(radians) * radius
        py = cy + math.sin(radians) * radius
        _leaf(
            f"{prefix}_petal_{index + 1}",
            px,
            py,
            scale * 0.92,
            scale * 0.42,
            angle,
            petal_color,
            line_width=0.24,
        )
    _dot(f"{prefix}_center", cx, cy, scale * 0.20, center_color, filled=True, width=0.08)


def _refine_monaco():
    for name in (
        "design__monaco_mast", "design__monaco_top", "design__monaco_diagonal",
        "design__monaco_signal", "design__monaco_bottom", "design__monaco_gold_dot",
    ):
        _hide(name)

    width, height = scribus.getPageSize()
    cx = width / 2.0
    mast_top = height * 0.036
    mast_bottom = height * 0.145

    # Abstract evening-regatta sail, centred like a fashion-house emblem rather
    # than a corporate border. Navy provides structure, gold/coral keep it bridal.
    _line("design__monaco_refined_mast", cx, mast_top, cx, mast_bottom, COLOR_ACCENT, 0.38)
    _polyline(
        "design__monaco_refined_sail_left",
        [cx, mast_top, width * 0.405, height * 0.132, cx, height * 0.132],
        COLOR_GOLD,
        0.30,
    )
    _polyline(
        "design__monaco_refined_sail_right",
        [cx, mast_top, width * 0.595, height * 0.132, cx, height * 0.132],
        COLOR_ACCENT,
        0.34,
    )
    _line(
        "design__monaco_refined_flag",
        cx + width * 0.012,
        height * 0.052,
        cx + width * 0.070,
        height * 0.052,
        COLOR_SECONDARY,
        0.78,
    )

    # Quiet lower signature echoes a yacht waterline but leaves the invitation
    # open and formal.
    y = height * 0.925
    _line("design__monaco_refined_lower_left", width * 0.35, y, cx - width * 0.025, y, COLOR_ACCENT, 0.24)
    _line("design__monaco_refined_lower_right", cx + width * 0.025, y, width * 0.65, y, COLOR_ACCENT, 0.24)
    _dot("design__monaco_refined_lower_mark", cx, y, min(width, height) * 0.008, COLOR_GOLD)


def _refine_provence():
    for name in (
        "design__provence_stem_top", "design__provence_leaf_1", "design__provence_leaf_2",
        "design__provence_bud", "design__provence_stem_bottom", "design__provence_leaf_3",
        "design__provence_bud_bottom", "design__provence_top_rule",
    ):
        _hide(name)

    width, height = scribus.getPageSize()

    # Upper-right branch: thin hand-drawn vector line with open leaves. It is
    # large enough to feel intentional but never becomes a full floral border.
    _polyline(
        "design__provence_refined_stem_top",
        _quadratic_points(
            (width * 0.825, height * 0.035),
            (width * 0.925, height * 0.105),
            (width * 0.955, height * 0.245),
        ),
        COLOR_GOLD,
        0.22,
    )
    upper_leaves = [
        (0.865, 0.080, 0.060, 0.018, 34, COLOR_SECONDARY),
        (0.895, 0.115, 0.052, 0.017, -24, COLOR_ACCENT),
        (0.918, 0.157, 0.057, 0.018, 32, COLOR_SECONDARY),
        (0.940, 0.202, 0.047, 0.016, -22, COLOR_ACCENT),
    ]
    for index, (x, y, length, leaf_w, angle, color) in enumerate(upper_leaves, 1):
        _leaf(
            f"design__provence_refined_leaf_top_{index}",
            width * x,
            height * y,
            width * length,
            height * leaf_w,
            angle,
            color,
        )
    _dot("design__provence_refined_bud_1", width * 0.946, height * 0.221, min(width, height) * 0.009, COLOR_ACCENT, filled=False, width=0.25)
    _dot("design__provence_refined_bud_2", width * 0.932, height * 0.184, min(width, height) * 0.007, COLOR_SECONDARY, filled=False, width=0.22)

    # Lower-left echo, deliberately smaller and lighter.
    _polyline(
        "design__provence_refined_stem_bottom",
        _quadratic_points(
            (width * 0.045, height * 0.805),
            (width * 0.075, height * 0.895),
            (width * 0.165, height * 0.950),
        ),
        COLOR_GOLD,
        0.18,
    )
    _leaf("design__provence_refined_leaf_bottom_1", width * 0.080, height * 0.875, width * 0.050, height * 0.016, -35, COLOR_ACCENT, 0.18)
    _leaf("design__provence_refined_leaf_bottom_2", width * 0.120, height * 0.918, width * 0.046, height * 0.015, 28, COLOR_SECONDARY, 0.18)
    _dot("design__provence_refined_bud_bottom", width * 0.055, height * 0.825, min(width, height) * 0.007, COLOR_ACCENT, filled=False, width=0.20)

    _line("design__provence_refined_top_rule", width * 0.405, height * 0.060, width * 0.595, height * 0.060, COLOR_GOLD, 0.20)


def _refine_riviera():
    for name in (
        "design__riviera_stem_top", "design__riviera_top_petal_1", "design__riviera_top_petal_2",
        "design__riviera_top_petal_3", "design__riviera_top_petal_4", "design__riviera_top_center",
        "design__riviera_leaf_top", "design__riviera_stem_bottom", "design__riviera_bottom_petal_1",
        "design__riviera_bottom_petal_2", "design__riviera_bottom_petal_3", "design__riviera_bottom_petal_4",
        "design__riviera_bottom_center", "design__riviera_gold_rule",
    ):
        _hide(name)

    width, height = scribus.getPageSize()
    scale = min(width, height) * 0.060

    # Upper-right open peony-like bloom: line art rather than filled icon petals.
    _polyline(
        "design__riviera_refined_stem_top",
        _quadratic_points(
            (width * 0.900, height * 0.035),
            (width * 0.865, height * 0.130),
            (width * 0.820, height * 0.245),
        ),
        COLOR_SECONDARY,
        0.24,
    )
    _outlined_flower(
        "design__riviera_refined_top",
        width * 0.885,
        height * 0.100,
        scale,
        COLOR_ACCENT,
        COLOR_GOLD,
        petal_count=7,
    )
    _leaf("design__riviera_refined_leaf_top_1", width * 0.850, height * 0.170, scale * 0.90, scale * 0.30, 28, COLOR_SECONDARY, 0.20)
    _leaf("design__riviera_refined_leaf_top_2", width * 0.830, height * 0.210, scale * 0.78, scale * 0.28, -32, COLOR_SECONDARY, 0.20)

    # Smaller lower-left blossom creates asymmetry without crowding the address.
    _polyline(
        "design__riviera_refined_stem_bottom",
        _quadratic_points(
            (width * 0.070, height * 0.955),
            (width * 0.090, height * 0.885),
            (width * 0.135, height * 0.805),
        ),
        COLOR_SECONDARY,
        0.20,
    )
    _outlined_flower(
        "design__riviera_refined_bottom",
        width * 0.095,
        height * 0.875,
        scale * 0.66,
        COLOR_TERTIARY,
        COLOR_GOLD,
        petal_count=5,
    )
    _leaf("design__riviera_refined_leaf_bottom", width * 0.115, height * 0.830, scale * 0.65, scale * 0.24, 34, COLOR_SECONDARY, 0.18)
    _line("design__riviera_refined_gold_rule", width * 0.38, height * 0.925, width * 0.62, height * 0.925, COLOR_GOLD, 0.20)


def _apply(theme):
    if theme == "monaco-regatta":
        _refine_monaco()
    elif theme == "provence-rose":
        _refine_provence()
    elif theme == "riviera-garden":
        _refine_riviera()
    else:
        raise RuntimeError(f"No refinement renderer for {theme}")


def main():
    root, theme = _args()
    marker = root / f"{MARKER_PREFIX}{theme}"
    if marker.exists():
        marker.unlink()

    templates = sorted(root.glob("*/invitation.sla"))
    if len(templates) != 2:
        raise RuntimeError(f"Expected two Invitation SLA templates, found {len(templates)}")

    for template in templates:
        scribus.openDoc(str(template))
        try:
            _apply(theme)
            scribus.saveDoc()
        finally:
            scribus.closeDoc()

    marker.write_text(f"theme={theme}\npiece=invitation\ntemplates=2\n", encoding="utf-8")
    print(f"Refined Invitation prototype '{theme}' in {len(templates)} templates.")


if __name__ == "__main__":
    main()
