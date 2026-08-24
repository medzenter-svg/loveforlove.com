"""Активная производственная конфигурация loveforlove.com.

Магазин и редактор используют только утвержденные 24 элемента Amalfi.
Никакие резервные позиции в интерфейс, JSON или печать не попадают.
"""

from cards_config import (
    CARDS_CONFIG as _SOURCE_CARDS,
    SUPPORTED_LANGUAGES,
    DEFAULT_BLEED_MM,
    printable_dimensions,
)

CARDS_CONFIG = [card for card in _SOURCE_CARDS if 1 <= card.get("number", 0) <= 24]

if len(CARDS_CONFIG) != 24:
    raise RuntimeError(f"Expected exactly 24 approved stationery items, got {len(CARDS_CONFIG)}")

CARDS_BY_ID = {card["id"]: card for card in CARDS_CONFIG}
