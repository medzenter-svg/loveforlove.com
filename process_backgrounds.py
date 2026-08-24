#!/usr/bin/env python3
"""
process_backgrounds.py

Standardizes the 24 hand/AI-composed Amalfi wedding stationery backgrounds
into print-ready WebP files at a strict 300 DPI.

This does NOT crop one master image into 24 shapes. Each of the 24 cards
already has its own individually composed artwork (corner lemon/flower/
greenery frame, sized and arranged for that specific card) — this script
just standardizes each one to the exact pixel size its card needs and
exports it correctly.

Usage (run from the repository root, after `git pull`):

    python3 process_backgrounds.py

Requirements:
    - Pillow  (pip install Pillow)
    - store/cards_config.py present (defines CARDS_CONFIG, the single
      source of truth for the 24 approved stationery items)
    - amalfi_sources/ present in the repository root, containing one
      image per card, named exactly "<card_id>.png" (or .jpg/.jpeg/.webp),
      e.g. amalfi_sources/01_save_the_date.png ... amalfi_sources/24_envelope_suite.png
      (see reference/amalfi_24_sizes_checklist.md for the full list of
      required filenames and target pixel sizes)

For every card in CARDS_CONFIG this script:
    1. Converts the card's physical size (w_mm x h_mm) to pixels at a
       strict 300 DPI:  pixels = mm * 300 / 25.4
    2. Loads amalfi_sources/<card_id>.(png|jpg|jpeg|webp).
       - If its aspect ratio already matches the target (within 1%), it is
         simply resized — nothing is cropped, since the composition was
         already made correct for that card.
       - If the aspect ratio is off, it is center-fit (ImageOps.fit) to
         the exact target size, and a warning is printed so you know which
         card's source wasn't generated at quite the right proportions.
    3. Saves the result as store/static/designs/amalfi/<card_id>.webp,
       with the DPI metadata hard-set to (300, 300).

Cards with no matching file in amalfi_sources/ are skipped (not fatal) —
so you can run this incrementally as you produce the 24 images, and a
clear summary at the end lists what's still missing.
"""

import os
import sys

from PIL import Image, ImageOps

# ---------------------------------------------------------------------------
# Paths (all resolved relative to this script's location, so it works
# regardless of the directory it's invoked from).
# ---------------------------------------------------------------------------
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
STORE_DIR = os.path.join(ROOT_DIR, "store")
SOURCES_DIR = os.path.join(ROOT_DIR, "amalfi_sources")
OUTPUT_DIR = os.path.join(STORE_DIR, "static", "designs", "amalfi")

DPI = 300
MM_PER_INCH = 25.4
ASPECT_TOLERANCE = 0.01  # 1% — above this, we center-crop instead of plain resize
SOURCE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")


def mm_to_px(mm):
    """Convert a physical millimeter length to pixels at a strict 300 DPI."""
    return round(mm * DPI / MM_PER_INCH)


def load_cards_config():
    """Import CARDS_CONFIG directly from store/cards_config.py."""
    if STORE_DIR not in sys.path:
        sys.path.insert(0, STORE_DIR)
    try:
        from cards_config import CARDS_CONFIG
    except ImportError as exc:
        sys.exit(
            f"Could not import CARDS_CONFIG from {STORE_DIR}/cards_config.py — "
            f"make sure you are running this from a full checkout of the repo.\n{exc}"
        )
    return CARDS_CONFIG


def find_source_file(card_id):
    for ext in SOURCE_EXTENSIONS:
        candidate = os.path.join(SOURCES_DIR, f"{card_id}{ext}")
        if os.path.isfile(candidate):
            return candidate
    return None


def process_card(card):
    card_id = card["id"]
    w_px = mm_to_px(card["w_mm"])
    h_px = mm_to_px(card["h_mm"])

    source_path = find_source_file(card_id)
    if not source_path:
        return "missing"

    source_image = Image.open(source_path).convert("RGB")
    sw, sh = source_image.size
    target_ratio = w_px / h_px
    source_ratio = sw / sh

    if abs(source_ratio - target_ratio) / target_ratio <= ASPECT_TOLERANCE:
        fitted = source_image.resize((w_px, h_px), Image.LANCZOS)
        note = ""
    else:
        fitted = ImageOps.fit(source_image, (w_px, h_px), method=Image.LANCZOS, centering=(0.5, 0.5))
        note = "  [!] aspect ratio mismatch — center-cropped, check the edges"

    out_path = os.path.join(OUTPUT_DIR, f"{card_id}.webp")
    fitted.save(out_path, format="WEBP", quality=95, dpi=(DPI, DPI))

    print(f"  {card_id:<24} {card['w_mm']:>4}x{card['h_mm']:<4}mm -> {w_px}x{h_px}px  ->  {out_path}{note}")
    return "ok"


def main():
    if not os.path.isdir(SOURCES_DIR):
        sys.exit(
            f"Sources folder not found: {SOURCES_DIR}\n"
            f"Create it and drop your 24 per-card images in there first "
            f"(see reference/amalfi_24_sizes_checklist.md for filenames)."
        )

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    cards = load_cards_config()
    print(f"Loaded {len(cards)} cards from store/cards_config.py\n")

    done, missing = [], []
    for card in cards:
        result = process_card(card)
        (done if result == "ok" else missing).append(card["id"])

    print(f"\nDone — {len(done)}/{len(cards)} backgrounds written to {OUTPUT_DIR}")
    if missing:
        print(f"\nStill missing ({len(missing)}) — no file found in {SOURCES_DIR}/:")
        for card_id in missing:
            print(f"  - {card_id}")


if __name__ == "__main__":
    main()
