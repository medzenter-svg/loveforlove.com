"""Registry of wedding visual themes used by the professional Scribus pipeline.

A catalog blueprint may exist before its print design is implemented. Only themes
with implemented=True may be applied to professional masters. This prevents a
planned collection from silently falling back to the Paris design and being sold
under a different name.
"""

DEFAULT_PREPRESS_THEME = "paris-editorial"

WEDDING_PREPRESS_THEMES = {
    "paris-editorial": {
        "implemented": True,
        "motif": "open_corners",
        "paper": (0, 1, 4, 1),
        "accent": (10, 180, 145, 150),
        "gold": (0, 40, 122, 63),
        "ink": (0, 27, 37, 207),
        "title_font": "EB Garamond 12 Regular",
        "body_font": "Lato Regular",
    },
    "amalfi-luce": {"implemented": False, "motif": "amalfi_arch"},
    "monaco-regatta": {"implemented": False, "motif": "regatta_rules"},
    "como-sereno": {"implemented": False, "motif": "lake_line"},
    "provence-rose": {"implemented": False, "motif": "botanical_punctuation"},
    "santorini-aegean": {"implemented": False, "motif": "aegean_arch_sun"},
    "riviera-garden": {"implemented": False, "motif": "asymmetric_floral"},
    "vienna-champagne": {"implemented": False, "motif": "ceremonial_crest"},
}


class PrepressThemeError(ValueError):
    pass


def get_prepress_theme(code, require_implemented=True):
    code = str(code or "").strip()
    theme = WEDDING_PREPRESS_THEMES.get(code)
    if theme is None:
        raise PrepressThemeError(f"Unknown wedding prepress theme: {code}")
    if require_implemented and not theme.get("implemented"):
        raise PrepressThemeError(
            f"Wedding prepress theme is still design-locked and cannot export: {code}"
        )
    return theme


def implemented_theme_codes():
    return {
        code for code, theme in WEDDING_PREPRESS_THEMES.items()
        if theme.get("implemented")
    }
