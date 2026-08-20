"""Validate Scribus SLA geometry and color-management setup before export."""

from __future__ import annotations

import math
import os
import xml.etree.ElementTree as ET
from pathlib import Path

from print_piece_specs import PRINT_PIECE_SPECS


MM_TO_PT = 72.0 / 25.4
IN_TO_PT = 72.0
TOLERANCE_PT = 0.75


class TemplatePreflightError(RuntimeError):
    pass


def _expected_geometry(size_family, piece):
    family = PRINT_PIECE_SPECS[size_family]
    spec = family["pieces"][piece]
    if "trim_mm" in spec:
        width, height = (v * MM_TO_PT for v in spec["trim_mm"])
        bleed = family["bleed_mm"] * MM_TO_PT
    else:
        width, height = (v * IN_TO_PT for v in spec["trim_in"])
        bleed = family["bleed_in"] * IN_TO_PT
    return width, height, bleed


def _float_attr(document, key):
    try:
        return float(document.attrib[key])
    except (KeyError, ValueError) as exc:
        raise TemplatePreflightError(f"Missing/invalid SLA attribute: {key}") from exc


def _near(actual, expected):
    return math.isclose(actual, expected, abs_tol=TOLERANCE_PT)


def validate_template(template_path, size_family, piece):
    template_path = Path(template_path)
    if not template_path.is_file():
        raise TemplatePreflightError(f"Template does not exist: {template_path}")

    try:
        root = ET.parse(template_path).getroot()
    except ET.ParseError as exc:
        raise TemplatePreflightError(f"Invalid SLA XML: {template_path}") from exc

    document = root.find("DOCUMENT")
    if document is None:
        raise TemplatePreflightError("SLA DOCUMENT element not found")

    expected_w, expected_h, expected_bleed = _expected_geometry(size_family, piece)
    actual_w = _float_attr(document, "PAGEWIDTH")
    actual_h = _float_attr(document, "PAGEHEIGHT")
    if not (_near(actual_w, expected_w) and _near(actual_h, expected_h)):
        raise TemplatePreflightError(
            f"Wrong page size for {piece}/{size_family}: "
            f"{actual_w:.2f}×{actual_h:.2f} pt, expected {expected_w:.2f}×{expected_h:.2f} pt"
        )

    for key in ("BleedTop", "BleedLeft", "BleedRight", "BleedBottom"):
        actual = _float_attr(document, key)
        if actual + TOLERANCE_PT < expected_bleed:
            raise TemplatePreflightError(
                f"{key} too small for {piece}/{size_family}: {actual:.2f} pt < {expected_bleed:.2f} pt"
            )

    if document.attrib.get("HCMS") != "1" or document.attrib.get("DPuse") != "1":
        raise TemplatePreflightError(
            "Color management is not enabled in this SLA (HCMS=1 and DPuse=1 required)."
        )

    required_profiles = {
        "DPPr": os.environ.get("LF_OUTPUT_PROFILE_NAME"),
        "DPIn": os.environ.get("LF_RGB_PROFILE_NAME"),
        "DPIn2": os.environ.get("LF_RGB_PROFILE_NAME"),
        "DPInCMYK": os.environ.get("LF_CMYK_PROFILE_NAME"),
        "DPIn3": os.environ.get("LF_CMYK_PROFILE_NAME"),
    }
    missing_env = [name for name, value in {
        "LF_OUTPUT_PROFILE_NAME": required_profiles["DPPr"],
        "LF_RGB_PROFILE_NAME": required_profiles["DPIn"],
        "LF_CMYK_PROFILE_NAME": required_profiles["DPInCMYK"],
    }.items() if not value]
    if missing_env:
        raise TemplatePreflightError(
            "Missing required CMS environment variables: " + ", ".join(missing_env)
        )

    for attr, expected in required_profiles.items():
        actual = document.attrib.get(attr)
        if actual != expected:
            raise TemplatePreflightError(
                f"SLA profile mismatch: {attr}={actual!r}, expected {expected!r}"
            )

    return True
