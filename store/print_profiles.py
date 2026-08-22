PRINT_PROFILES = {
    "pdfx4_worldwide": {
        "name": "Professional Master — PDF/X-4",
        "purpose": "Primary master for modern commercial and digital print workflows worldwide.",
        "standard": "PDF/X-4",
        "raster_resolution": "300 DPI minimum at final size",
        "bleed_eu_mm": 3,
        "bleed_us_in": 0.125,
        "safe_area_mm": 5,
        "trim_box": True,
        "bleed_box": True,
        "fonts": "embedded; signature/display lettering may be outlined in final export",
        "vector_policy": "keep text, borders, ornaments and monograms vector whenever possible",
        "transparency": "preserve live transparency where supported by PDF/X-4",
        "color_policy": "ICC color-managed PDF with an output intent; receiving printer may convert to its own press/paper condition",
        "crop_marks": "separate marked export may be generated only when requested by the printer",
    },
    "pdfx1a_compatibility": {
        "name": "Compatibility Master — PDF/X-1a",
        "purpose": "Fallback for older commercial print workflows that do not accept PDF/X-4.",
        "standard": "PDF/X-1a",
        "raster_resolution": "300 DPI minimum at final size",
        "bleed_eu_mm": 3,
        "bleed_us_in": 0.125,
        "safe_area_mm": 5,
        "trim_box": True,
        "bleed_box": True,
        "fonts": "embedded or outlined",
        "vector_policy": "preserve vector geometry where compatible",
        "transparency": "flatten according to compatibility workflow",
        "color_policy": "CMYK/spot-compatible export with output intent",
        "crop_marks": "separate marked export may be generated only when requested by the printer",
    },
}

WORLDWIDE_PRINT_PACKAGE = [
    "One separate professional file for every printed piece",
    "PDF/X-4 master for modern printers",
    "PDF/X-1a compatibility master for older workflows",
    "3 mm bleed version for metric/European production",
    "0.125 in bleed version for North American production",
    "Defined TrimBox and BleedBox",
    "300 DPI minimum raster artwork at final size",
    "Vector text, ornaments, borders and monograms wherever possible",
    "Embedded fonts or outlined display lettering",
    "ICC color-managed output with output intent",
    "Print specification sheet identifying finished size and bleed for each piece",
]

# No single fixed CMYK conversion can represent every press, paper stock and region.
# The professional master should therefore remain color managed and carry an output
# intent. The receiving print shop can apply its exact press/paper ICC conversion
# without rebuilding the design.
