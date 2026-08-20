"""Registry of wedding visual themes used by the professional Scribus pipeline.

A catalog blueprint may exist before its print design is implemented. Only themes
with implemented=True may be applied to professional customer masters. A theme may
have prototype_ready=True for an isolated visual/print prototype while remaining
blocked from full-package export and sale.
"""

DEFAULT_PREPRESS_THEME = "paris-editorial"

WEDDING_PREPRESS_THEMES = {
    "paris-editorial": {
        "implemented": True,
        "prototype_ready": True,
        "motif": "open_corners",
        "paper": (0, 1, 4, 1),
        "accent": (10, 180, 145, 150),
        "gold": (0, 40, 122, 63),
        "ink": (0, 27, 37, 207),
        "title_font": "EB Garamond 12 Regular",
        "body_font": "Lato Regular",
    },
    "amalfi-luce": {
        "implemented": False,
        "prototype_ready": True,
        "prototype_piece": "invitation",
        "motif": "amalfi_arch",
        # Bright Mediterranean paper, bougainvillea coral, olive and champagne.
        # Scribus uses CMYK values in the 0..255 range.
        "paper": (0, 1, 5, 0),
        "accent": (0, 145, 115, 42),
        "secondary": (95, 62, 122, 92),
        "gold": (0, 36, 104, 52),
        "ink": (30, 34, 38, 205),
        "title_font": "EB Garamond 12 Regular",
        "body_font": "Lato Regular",
    },
    "monaco-regatta": {"implemented": False, "prototype_ready": False, "motif": "regatta_rules"},
    "como-sereno": {"implemented": False, "prototype_ready": False, "motif": "lake_line"},
    "provence-rose": {"implemented": False, "prototype_ready": False, "motif": "botanical_punctuation"},
    "santorini-aegean": {"implemented": False, "prototype_ready": False, "motif": "aegean_arch_sun"},
    "riviera-garden": {"implemented": False, "prototype_ready": False, "motif": "asymmetric_floral"},
    "vienna-champagne": {"implemented": False, "prototype_ready": False, "motif": "ceremonial_crest"},
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


def get_prototype_theme(code, piece):
    theme = get_prepress_theme(code, require_implemented=False)
    if not theme.get("prototype_ready"):
        raise PrepressThemeError(f"Wedding theme has no approved prototype path: {code}")
    expected_piece = theme.get("prototype_piece")
    if expected_piece and expected_piece != piece:
        raise PrepressThemeError(
            f"Wedding theme prototype is limited to {expected_piece}, not {piece}: {code}"
        )
    return theme


def implemented_theme_codes():
    return {
        code for code, theme in WEDDING_PREPRESS_THEMES.items()
        if theme.get("implemented")
    }
