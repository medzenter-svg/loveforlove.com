"""Генерация типографских PDF и ZIP-пакета через Playwright/Chromium.

PDF сохраняет векторный текст и CSS. Понятие 300 DPI относится только к растровым
фоновым изображениям: исходные PNG/WebP должны иметь достаточное разрешение.
"""

from __future__ import annotations

import base64
import mimetypes
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Callable

from playwright.sync_api import sync_playwright

from cards_config import EXPECTED_CARD_COUNT, printable_dimensions

PACKAGE_FILENAME = "loveforlove_wedding_package.zip"


def _safe_filename(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_")
    return value or "card"


def _file_data_uri(path: Path) -> str | None:
    if not path.is_file():
        return None
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def resolve_background_uri(static_root: str, design_id: str, card_id: str) -> str | None:
    """Встраивает фон текущего дизайна как data URI."""
    base = Path(static_root) / "designs" / _safe_filename(design_id)
    for extension in ("webp", "png", "jpg", "jpeg"):
        uri = _file_data_uri(base / f"{card_id}.{extension}")
        if uri:
            return uri
    return None


def resolve_font_uris(static_root: str) -> dict[str, str | None]:
    """Возвращает локальные шрифты для автономной печати Chromium.

    Предпочтителен WOFF2. Если его нет, используется TTF с тем же именем.
    """
    fonts_root = Path(static_root) / "fonts"

    def choose(stem: str) -> str | None:
        for extension in ("woff2", "ttf"):
            uri = _file_data_uri(fonts_root / f"{stem}.{extension}")
            if uri:
                return uri
        return None

    return {
        "cormorant_regular": choose("CormorantGaramond-Regular"),
        "cormorant_semibold": choose("CormorantGaramond-SemiBold"),
        "allura_regular": choose("Allura-Regular"),
    }


def generate_wedding_package(
    *,
    cards_config: list[dict],
    normalized_cards: list[dict],
    language: str,
    design_id: str,
    downloads_dir: str,
    order_id: str,
    static_root: str,
    render_card_html: Callable[..., str],
) -> str:
    """Создает 24 PDF и упаковывает их в ZIP.

    Отдельные PDF живут только во временном каталоге и удаляются автоматически.
    В downloads/<order_id>/ остается только loveforlove_wedding_package.zip.
    """
    if len(cards_config) != EXPECTED_CARD_COUNT:
        raise ValueError("Server configuration must contain exactly 24 cards")
    if len(normalized_cards) != EXPECTED_CARD_COUNT:
        raise ValueError("Payload must contain exactly 24 cards")

    expected_ids = [card["id"] for card in cards_config]
    submitted_ids = [item["id"] for item in normalized_cards]
    if submitted_ids != expected_ids:
        raise ValueError("Card ids/order do not match server configuration")
    by_id = {item["id"]: item for item in normalized_cards}

    order_dir = Path(downloads_dir) / _safe_filename(order_id)
    order_dir.mkdir(parents=True, exist_ok=True)
    zip_path = order_dir / PACKAGE_FILENAME

    if zip_path.exists():
        zip_path.unlink()

    font_uris = resolve_font_uris(static_root)

    with tempfile.TemporaryDirectory(prefix="loveforlove_pdf_") as temp_dir:
        temp_path = Path(temp_dir)
        pdf_paths: list[Path] = []

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page()

                for index, card in enumerate(cards_config, start=1):
                    submitted = by_id[card["id"]]
                    dimensions = printable_dimensions(card)
                    page_w_mm = dimensions["page_w_mm"]
                    page_h_mm = dimensions["page_h_mm"]
                    background_uri = resolve_background_uri(
                        static_root,
                        design_id,
                        card["id"],
                    )

                    html = render_card_html(
                        card=card,
                        values=submitted["values"],
                        views=card.get("views") or ["front"],
                        language=language,
                        design_id=design_id,
                        background_uri=background_uri,
                        font_uris=font_uris,
                        dimensions=dimensions,
                    )

                    page.set_content(html, wait_until="load")
                    page.emulate_media(media="print")
                    page.evaluate("document.fonts ? document.fonts.ready : Promise.resolve()")

                    pdf_name = f"{index:02d}_{_safe_filename(card['id'])}.pdf"
                    pdf_path = temp_path / pdf_name

                    page.pdf(
                        path=str(pdf_path),
                        width=f"{page_w_mm}mm",
                        height=f"{page_h_mm}mm",
                        print_background=True,
                        prefer_css_page_size=True,
                        margin={
                            "top": "0mm",
                            "right": "0mm",
                            "bottom": "0mm",
                            "left": "0mm",
                        },
                    )
                    pdf_paths.append(pdf_path)
            finally:
                browser.close()

        if len(pdf_paths) != EXPECTED_CARD_COUNT:
            raise RuntimeError("PDF generator did not produce exactly 24 files")

        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for pdf_path in pdf_paths:
                archive.write(pdf_path, arcname=pdf_path.name)

    if not zip_path.is_file():
        raise RuntimeError("ZIP package was not created")

    return str(zip_path)
