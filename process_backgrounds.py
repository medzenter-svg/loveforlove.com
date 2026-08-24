#!/usr/bin/env python3
"""
process_backgrounds.py

Generates all 24 print-ready WebP backgrounds for the Amalfi wedding
stationery collection from a single reference artwork file.

Usage (run from the repository root, after `git pull`):

    python3 process_backgrounds.py

Requirements:
    - Pillow  (pip install Pillow)
    - store/cards_config.py present (defines CARDS_CONFIG, the single
      source of truth for the 24 approved stationery items)
    - source_amalfi.png present in the repository root (your reference
      artwork)

For every card in CARDS_CONFIG this script:
    1. Converts the card's physical size (w_mm x h_mm) to pixels at a
       strict 300 DPI:  pixels = mm * 300 / 25.4
    2. Proportionally scales + center-crops source_amalfi.png to those
       exact pixel dimensions (ImageOps.fit), so nothing is distorted
       and nothing is left transparent/empty.
    3. Saves the result as store/static/designs/amalfi/<card_id>.webp,
       with the DPI metadata hard-set to (300, 300).

Card #24 (Envelope Suite) needs no special-casing: its CARDS_CONFIG
entry already stores the full flat die-line size (255 x 365 mm) in
w_mm/h_mm, so the same mm -> px -> fit -> save pipeline automatically
produces the correct oversized canvas for it.
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
SOURCE_IMAGE_PATH = os.path.join(ROOT_DIR, "source_amalfi.png")
OUTPUT_DIR = os.path.join(STORE_DIR, "static", "designs", "amalfi")

DPI = 300
MM_PER_INCH = 25.4


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


def process_card(source_image, card):
    card_id = card["id"]
    w_px = mm_to_px(card["w_mm"])
    h_px = mm_to_px(card["h_mm"])

    # Proportionally scale + center-crop to the exact target size — never
    # distorts the artwork, never leaves empty/transparent margins.
    fitted = ImageOps.fit(source_image, (w_px, h_px), method=Image.LANCZOS, centering=(0.5, 0.5))

    out_path = os.path.join(OUTPUT_DIR, f"{card_id}.webp")
    fitted.save(out_path, format="WEBP", quality=95, dpi=(DPI, DPI))

    print(f"  {card_id:<24} {card['w_mm']:>4}x{card['h_mm']:<4}mm -> {w_px}x{h_px}px  ->  {out_path}")


def main():
    if not os.path.isfile(SOURCE_IMAGE_PATH):
        sys.exit(
            f"Reference artwork not found: {SOURCE_IMAGE_PATH}\n"
            f"Place your source_amalfi.png in the repository root and run again."
        )

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    cards = load_cards_config()
    print(f"Loaded {len(cards)} cards from store/cards_config.py")

    source_image = Image.open(SOURCE_IMAGE_PATH).convert("RGB")
    print(f"Source artwork: {SOURCE_IMAGE_PATH} ({source_image.width}x{source_image.height}px)\n")

    for card in cards:
        process_card(source_image, card)

    print(f"\nDone — {len(cards)} backgrounds written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
