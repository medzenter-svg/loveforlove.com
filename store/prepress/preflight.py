"""Structural preflight for exported professional PDFs.

This is intentionally a conservative QA gate, not a substitute for a certified
PDF/X validator used by a print provider. It verifies file integrity, page boxes,
font embedding and PDF/X identification using standard prepress tools.
"""

from __future__ import annotations

import math
import re
import shutil
import subprocess
from pathlib import Path

from print_piece_specs import PRINT_PIECE_SPECS


MM_TO_PT = 72.0 / 25.4
IN_TO_PT = 72.0
TOLERANCE_PT = 0.75


class PreflightError(RuntimeError):
    pass


def _run(command):
    proc = subprocess.run(command, text=True, capture_output=True)
    if proc.returncode != 0:
        raise PreflightError(
            f"Command failed ({' '.join(command)}):\n{proc.stdout}\n{proc.stderr}"
        )
    return proc.stdout


def _require_tool(name):
    path = shutil.which(name)
    if not path:
        raise PreflightError(f"Required prepress tool is not installed: {name}")
    return path


def _expected_trim_points(size_family, piece):
    spec = PRINT_PIECE_SPECS[size_family]["pieces"][piece]
    if "trim_mm" in spec:
        return tuple(value * MM_TO_PT for value in spec["trim_mm"])
    return tuple(value * IN_TO_PT for value in spec["trim_in"])


def _expected_bleed_points(size_family):
    family = PRINT_PIECE_SPECS[size_family]
    if "bleed_mm" in family:
        return family["bleed_mm"] * MM_TO_PT
    return family["bleed_in"] * IN_TO_PT


def _parse_box(pdfinfo_text, label):
    match = re.search(
        rf"^{re.escape(label)}:\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)",
        pdfinfo_text,
        flags=re.MULTILINE,
    )
    if not match:
        raise PreflightError(f"{label} not found in PDF")
    x1, y1, x2, y2 = map(float, match.groups())
    return x1, y1, x2, y2


def _box_size(box):
    x1, y1, x2, y2 = box
    return abs(x2 - x1), abs(y2 - y1)


def _near(a, b, tolerance=TOLERANCE_PT):
    return math.isclose(a, b, abs_tol=tolerance)


def _check_page_boxes(pdf_path, size_family, piece):
    pdfinfo = _require_tool("pdfinfo")
    info = _run([pdfinfo, "-box", str(pdf_path)])
    trim = _parse_box(info, "TrimBox")
    bleed = _parse_box(info, "BleedBox")

    trim_w, trim_h = _box_size(trim)
    expected_w, expected_h = _expected_trim_points(size_family, piece)

    if not (_near(trim_w, expected_w) and _near(trim_h, expected_h)):
        raise PreflightError(
            f"Unexpected TrimBox for {piece}/{size_family}: "
            f"{trim_w:.2f}×{trim_h:.2f} pt; expected "
            f"{expected_w:.2f}×{expected_h:.2f} pt"
        )

    bleed_w, bleed_h = _box_size(bleed)
    required = _expected_bleed_points(size_family) * 2
    if bleed_w + TOLERANCE_PT < trim_w + required or bleed_h + TOLERANCE_PT < trim_h + required:
        raise PreflightError(
            f"BleedBox is too small for {piece}/{size_family}: "
            f"Trim {trim_w:.2f}×{trim_h:.2f}, Bleed {bleed_w:.2f}×{bleed_h:.2f} pt"
        )


def _check_fonts(pdf_path):
    pdffonts = _require_tool("pdffonts")
    output = _run([pdffonts, str(pdf_path)])
    lines = [line for line in output.splitlines() if line.strip()]
    if len(lines) <= 2:
        return

    # pdffonts rows end with: emb sub uni object-ID generation-ID.
    # Type names can contain spaces, so parsing from the right is stable.
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("name") or stripped.startswith("---"):
            continue
        columns = stripped.split()
        if len(columns) < 5:
            raise PreflightError(f"Cannot parse pdffonts row: {line}")
        embedded = columns[-5].lower()
        if embedded != "yes":
            raise PreflightError(f"Unembedded font detected: {line}")


def _check_pdf_integrity(pdf_path):
    gs = _require_tool("gs")
    _run([gs, "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=nullpage", str(pdf_path)])


def _check_pdfx_marker(pdf_path, profile):
    exiftool = _require_tool("exiftool")
    metadata = _run([exiftool, "-s", "-G1", str(pdf_path)])
    expected = "PDF/X-4" if profile == "pdfx4_worldwide" else "PDF/X-1"

    # Different generators expose this under slightly different XMP/Info tags.
    pdfx_lines = [
        line for line in metadata.splitlines()
        if "PDFX" in line.upper() or "GTS_PDFX" in line.upper()
    ]
    joined = "\n".join(pdfx_lines)
    if expected not in joined:
        raise PreflightError(
            f"Expected {expected} identification not found in metadata for {pdf_path.name}. "
            f"PDF/X metadata seen: {joined or 'none'}"
        )


def preflight_pdf(pdf_path, size_family, piece, profile):
    pdf_path = Path(pdf_path)
    if not pdf_path.is_file():
        raise PreflightError(f"PDF does not exist: {pdf_path}")
    if pdf_path.stat().st_size < 1024:
        raise PreflightError(f"PDF is suspiciously small: {pdf_path}")

    _check_pdf_integrity(pdf_path)
    _check_page_boxes(pdf_path, size_family, piece)
    _check_fonts(pdf_path)
    _check_pdfx_marker(pdf_path, profile)
    return True
