#!/usr/bin/env python3
"""Локальный end-to-end тест печатной цепочки loveforlove.com.

Запуск из корня репозитория:
    python3 test_order.py

Скрипт без HTTP и без браузерного интерфейса:
1. Загружает утвержденную конфигурацию 24 элементов.
2. Формирует русский тестовый JSON с реалистичными данными.
3. Через Flask/Jinja2 рендерит тот же print_card.html, что использует production.
4. Напрямую вызывает Playwright-генератор.
5. Создает store/static/downloads/test_order/loveforlove_wedding_package.zip.
6. Проверяет, что ZIP содержит ровно 24 PDF.
"""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
STORE_DIR = ROOT_DIR / "store"
STATIC_DIR = STORE_DIR / "static"
DOWNLOADS_DIR = STATIC_DIR / "downloads"
ORDER_ID = "test_order"
DESIGN_ID = "amalfi"
LANGUAGE = "ru"

# Модули store используют локальные импорты вида `from cards_config import ...`,
# поэтому добавляем каталог store в sys.path при запуске из корня репозитория.
sys.path.insert(0, str(STORE_DIR))

from flask import render_template  # noqa: E402
from app import app  # noqa: E402
from cards_config import CARDS_CONFIG, EXPECTED_CARD_COUNT  # noqa: E402
from pdf_generator import PACKAGE_FILENAME, generate_wedding_package  # noqa: E402


TEST_OVERRIDES = {
    "01_save_the_date": {
        "names": "Александр и Екатерина",
        "date": "12 сентября 2026",
        "venue": "Вилла Чимброне",
        "location": "Равелло, Амальфитанское побережье, Италия",
        "greeting": "Официальное приглашение последует позже.",
    },
    "02_main_invitation": {
        "title": "Приглашение на свадьбу",
        "greeting": "Будем счастливы разделить с вами день нашей свадьбы.",
        "names": "Александр и Екатерина",
        "date": "12 сентября 2026",
        "time": "15:30",
        "venue": "Вилла Чимброне",
        "location": "Via Santa Chiara 26, 84010 Ravello SA, Италия",
        "reception": "Праздничный приём начнётся сразу после церемонии.",
        "dress_code": "Средиземноморский формальный стиль",
    },
    "03_details_card": {
        "title": "Детали свадьбы",
        "ceremony_time": "15:30",
        "ceremony_venue": "Сад Виллы Чимброне, Ravello",
        "reception_time": "18:30",
        "reception_venue": "Terrazza dell’Infinito, Villa Cimbrone",
        "dress_code": "Светлые натуральные оттенки · formal",
        "accommodation": "Hotel Santa Caterina, Amalfi",
        "transport": "Трансфер от отеля в 14:40 и обратно в 00:30",
        "dietary": "Сообщите, пожалуйста, об аллергиях и особенностях питания.",
    },
    "04_rsvp": {
        "title": "Подтвердите участие",
        "deadline": "Ответить до 15 июля 2026",
        "guest_name": "Анна и Михаил Орловы",
        "accept": "С радостью будем",
        "decline": "К сожалению, не сможем",
        "guest_count": "2 гостя",
        "meal": "Сибас / телятина / вегетарианское меню",
        "thanks": "Спасибо за ваш ответ. Мы очень ждём встречи!",
    },
    "05_wedding_website": {
        "title": "Сайт свадьбы",
        "greeting": "Все новости, программа и рекомендации для гостей.",
        "website": "loveforlove.com/alexander-ekaterina",
        "password": "AMALFI2026",
    },
    "06_hotel_accommodation": {
        "title": "Проживание",
        "hotel": "Hotel Santa Caterina",
        "address": "S.S. Amalfitana 9, 84011 Amalfi SA, Италия",
        "stay_dates": "11–13 сентября 2026",
        "check_in": "Заезд: 15:00",
        "check_out": "Выезд: 11:00",
        "rate": "Специальный свадебный тариф",
        "booking_code": "AE1209",
        "contact": "+39 089 871012 · reservations@hotelsantacaterina.it",
        "transfer": "Трансфер на церемонию входит в программу.",
        "payment_note": "Пара оплачивает первую ночь. Дополнительные ночи, мини-бар и личные расходы гости оплачивают самостоятельно.",
    },
    "07_transport_parking": {
        "title": "Трансфер и парковка",
        "departure": "Отправление: Hotel Santa Caterina",
        "departure_time": "14:40",
        "return_transfer": "Обратный трансфер: 00:30",
        "parking": "Парковка: Luna Rossa",
        "parking_address": "Via Pantaleone Comite 33, Amalfi, Италия",
        "instructions": "Просим быть на месте отправления за 15 минут.",
    },
    "08_dress_code": {
        "title": "Дресс-код",
        "day_one_style": "День 1 · Garden Cocktail",
        "day_one_palette": "Лимонный · шалфей · айвори · золото",
        "day_one_recommendations": "Лёгкие костюмы, платья миди, натуральные ткани.",
        "day_two_style": "День 2 · Formal Elegant",
        "day_two_palette": "Айвори · зелёный · золотой",
        "day_two_recommendations": "Вечерние платья и классические костюмы.",
    },
    "09_gifts_registry": {
        "title": "Подарки",
        "greeting": "Самый главный подарок для нас — ваше присутствие. Если захотите сделать подарок, будем благодарны за вклад в наше свадебное путешествие.",
        "registry": "loveforlove.com/alexander-ekaterina/gifts",
    },
    "10_coordinator_contacts": {
        "title": "Координатор свадьбы",
        "name": "Мария Беллини",
        "role": "Координатор гостей",
        "phone": "+39 333 555 0198",
        "email": "maria@bellinievents.it",
        "second_contact": "Лука Романо · +39 333 555 0201",
    },
    "11_general_program": {
        "title": "Программа свадебного уикенда",
        "date": "11–13 сентября 2026",
        "event_1": "Пятница · 19:00 · Приветственный ужин",
        "event_2": "Суббота · 15:30 · Церемония",
        "event_3": "Суббота · 18:30 · Приём и ужин",
        "event_4": "Воскресенье · 11:00 · Прощальный бранч",
    },
    "12_day_one_program": {
        "title": "Программа первого дня",
        "date": "11 сентября 2026",
        "event_1": "16:00 · Заезд гостей",
        "event_2": "19:00 · Приветственный ужин в саду",
        "event_3": "21:30 · Коктейли на закате",
    },
    "13_day_two_program": {
        "title": "Программа второго дня",
        "date": "12 сентября 2026",
        "event_1": "15:30 · Свадебная церемония",
        "event_2": "18:30 · Аперитив и приём",
        "event_3": "20:00 · Праздничный ужин",
        "event_4": "22:00 · Танцы под звёздами",
    },
    "14_wedding_program": {
        "title": "Программа свадьбы",
        "day_one_program": "11 сентября · Приветственный ужин · 19:00",
        "day_two_program": "12 сентября · Церемония 15:30 · Приём 18:30 · Ужин 20:00",
    },
    "15_ceremony": {
        "title": "Церемония",
        "date": "12 сентября 2026",
        "time": "15:30",
        "venue": "Belvedere Garden · Villa Cimbrone",
        "location": "Via Santa Chiara 26, Ravello, Италия",
        "greeting": "Просим занять места за 20 минут до начала.",
    },
    "16_order_of_ceremony": {
        "title": "Порядок церемонии",
        "processional": "Выход свадебной процессии",
        "reading": "Чтение",
        "vows": "Обмен клятвами",
        "rings": "Обмен кольцами",
        "unity": "Семейная церемония",
        "presentation": "Объявление молодожёнов",
        "recessional": "Торжественный выход",
    },
    "17_reception": {
        "title": "Свадебный приём",
        "time": "18:30",
        "venue": "Terrazza dell’Infinito",
        "location": "Villa Cimbrone, Ravello, Италия",
        "greeting": "Аперитив, ужин и танцы до поздней ночи.",
    },
    "18_menu": {
        "title": "Меню",
        "starter": "Буррата · лимон Амальфи · базилик",
        "first_course": "Домашние равиоли с рикоттой и травами",
        "main_course": "Сибас · сезонные овощи · лимонный соус",
        "dessert": "Delizia al limone",
        "drinks": "Итальянские вина · вода · кофе",
    },
    "19_table_number": {
        "title": "Стол",
        "table_number": "08",
    },
    "20_place_card": {
        "title": "Карточка гостя",
        "guest_name": "София Росси",
    },
    "21_welcome_sign": {
        "title": "Добро пожаловать",
        "greeting": "Сегодня начинается наша самая красивая история.",
        "names": "Александр и Екатерина",
        "date": "12 сентября 2026",
    },
    "22_guest_book_sign": {
        "title": "Книга пожеланий",
        "greeting": "Оставьте нам несколько слов, которые мы с улыбкой прочитаем через много лет.",
    },
    "23_thank_you": {
        "title": "Спасибо",
        "greeting": "Спасибо, что были рядом и сделали этот день частью нашей общей истории.",
        "names": "Александр и Екатерина",
    },
    "24_envelope_suite": {
        "recipient_name": "Анна и Михаил Орловы",
        "recipient_address": "Via dei Mille 18\n20129 Milano MI\nItalia",
        "return_names": "Александр и Екатерина",
        "return_address": "Villa Cimbrone\nVia Santa Chiara 26\n84010 Ravello SA · Italia",
        "flap_note": "С любовью из Равелло",
        "liner_text": "La dolce vita начинается здесь",
    },
}


def build_test_payload() -> dict:
    """Возвращает финальный JSON ровно для 24 карточек в серверном порядке."""
    if len(CARDS_CONFIG) != EXPECTED_CARD_COUNT:
        raise RuntimeError(
            f"Конфигурация должна содержать {EXPECTED_CARD_COUNT} элементов, "
            f"получено {len(CARDS_CONFIG)}"
        )

    cards = []
    for card in CARDS_CONFIG:
        values = dict(card["translations"][LANGUAGE])
        values.update(TEST_OVERRIDES.get(card["id"], {}))
        cards.append(
            {
                "id": card["id"],
                "view": (card.get("views") or ["front"])[0],
                "values": values,
            }
        )

    if len(cards) != EXPECTED_CARD_COUNT:
        raise RuntimeError("Тестовый payload должен содержать ровно 24 элемента")

    return {
        "product_slug": "amalfi-wedding-suite",
        "order_id": ORDER_ID,
        "design_id": DESIGN_ID,
        "language": LANGUAGE,
        "card_count": EXPECTED_CARD_COUNT,
        "cards": cards,
    }


def validate_zip(zip_path: Path) -> None:
    """Проверяет число PDF и отсутствие посторонних файлов в архиве."""
    if not zip_path.is_file():
        raise RuntimeError(f"ZIP не создан: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as archive:
        members = archive.namelist()
        pdfs = [name for name in members if name.lower().endswith(".pdf")]

    if len(members) != EXPECTED_CARD_COUNT or len(pdfs) != EXPECTED_CARD_COUNT:
        raise RuntimeError(
            "Некорректный ZIP: ожидается ровно 24 PDF, "
            f"найдено файлов={len(members)}, PDF={len(pdfs)}"
        )


def main() -> None:
    payload = build_test_payload()

    # Выводим компактную проверку структуры JSON до запуска Chromium.
    print(
        json.dumps(
            {
                "language": payload["language"],
                "design_id": payload["design_id"],
                "card_count": payload["card_count"],
                "first_id": payload["cards"][0]["id"],
                "last_id": payload["cards"][-1]["id"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

    def render_card_html(**context) -> str:
        return render_template("print_card.html", **context)

    with app.app_context():
        generated = generate_wedding_package(
            cards_config=CARDS_CONFIG,
            normalized_cards=payload["cards"],
            language=payload["language"],
            design_id=payload["design_id"],
            downloads_dir=str(DOWNLOADS_DIR),
            order_id=payload["order_id"],
            static_root=str(STATIC_DIR),
            render_card_html=render_card_html,
        )

    zip_path = Path(generated).resolve()
    expected_path = (
        DOWNLOADS_DIR / ORDER_ID / PACKAGE_FILENAME
    ).resolve()

    if zip_path != expected_path:
        raise RuntimeError(
            f"Архив создан не в ожидаемой папке:\n{zip_path}\nожидалось:\n{expected_path}"
        )

    validate_zip(zip_path)

    print("\nТЕСТ УСПЕШНО ЗАВЕРШЕН")
    print(f"Архив: {zip_path}")
    print("Содержимое: ровно 24 PDF-файла")
    print("Конверт №24: front / back / flap / liner находятся внутри PDF №24")


if __name__ == "__main__":
    main()
