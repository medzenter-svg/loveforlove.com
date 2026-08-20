from pathlib import Path

from print_piece_specs import PRINT_PIECE_SPECS
from print_profiles import PRINT_PROFILES


PIECE_ORDER = [
    "invitation",
    "venue_address",
    "rsvp",
    "menu",
    "table_number",
    "place_card",
    "program",
    "thank_you",
    "accommodation",
    "coordinator",
    "dress_code",
    "envelope",
    "envelope_liner",
    "program_day_1",
    "program_day_2",
]

OPTIONAL_PIECES = {
    "accommodation",
    "coordinator",
    "dress_code",
    "envelope",
    "envelope_liner",
    "program_day_1",
    "program_day_2",
}

PROFILE_CODES = {
    "pdfx4_worldwide": "PDFX4",
    "pdfx1a_compatibility": "PDFX1A",
}

SIZE_CODES = {
    "international_metric": "METRIC",
    "north_america": "NA",
}


def expected_filename(collection_slug, piece, size_family, profile):
    return f"{collection_slug}__{piece}__{SIZE_CODES[size_family]}__{PROFILE_CODES[profile]}.pdf"


def build_manifest(collection_slug, enabled_optional=None):
    enabled_optional = set(OPTIONAL_PIECES if enabled_optional is None else enabled_optional)
    manifest = []

    for piece in PIECE_ORDER:
        if piece in OPTIONAL_PIECES and piece not in enabled_optional:
            continue
        for size_family, size_spec in PRINT_PIECE_SPECS.items():
            if piece not in size_spec["pieces"]:
                raise ValueError(f"Missing size specification for {piece} in {size_family}")
            for profile in PRINT_PROFILES:
                manifest.append({
                    "piece": piece,
                    "optional": piece in OPTIONAL_PIECES,
                    "size_family": size_family,
                    "print_profile": profile,
                    "filename": expected_filename(collection_slug, piece, size_family, profile),
                    "size_spec": size_spec["pieces"][piece],
                    "profile_spec": PRINT_PROFILES[profile],
                })
    return manifest


def validate_package_directory(collection_slug, package_dir, enabled_optional=None):
    package_dir = Path(package_dir)
    expected = build_manifest(collection_slug, enabled_optional)
    missing = []
    empty = []

    for item in expected:
        file_path = package_dir / item["filename"]
        if not file_path.exists():
            missing.append(item["filename"])
        elif file_path.stat().st_size == 0:
            empty.append(item["filename"])

    expected_names = {item["filename"] for item in expected}
    unexpected = sorted(
        p.name for p in package_dir.glob("*.pdf")
        if p.name not in expected_names
    ) if package_dir.exists() else []

    return {
        "ok": not missing and not empty,
        "expected_count": len(expected),
        "present_count": len(expected) - len(missing),
        "missing": missing,
        "empty": empty,
        "unexpected": unexpected,
    }


def package_summary(collection_slug, enabled_optional=None):
    manifest = build_manifest(collection_slug, enabled_optional)
    by_piece = {}
    for item in manifest:
        by_piece.setdefault(item["piece"], 0)
        by_piece[item["piece"]] += 1
    return {
        "collection": collection_slug,
        "printable_pieces": len(by_piece),
        "professional_pdf_files": len(manifest),
        "files_per_piece": 4,
        "piece_counts": by_piece,
    }


if __name__ == "__main__":
    summary = package_summary("example-collection")
    print(summary)
