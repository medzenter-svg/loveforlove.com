# loveforlove.com

Digitale, romantische Produkte für Paare — Grußkarten, Coupons, Hochzeits-Papeterie, Menüs und mehr.

Jedes fertige Produkt trägt eine kleine Marke: **"Designed by loveforlove.com"**.

## Struktur

```
products/
  <produkt-name>/
    <Produktname>.pdf        ← fertige, verkaufsfertige Datei
    source/                  ← Quelldateien (Skripte, HTML, Rohdaten) zur Bearbeitung
```

## Produkte

| Produkt | Status | Datei |
|---|---|---|
| The Love Coupon Book | ✅ fertig | [products/love-coupon-book/Love_Coupons_loveforlove.pdf](products/love-coupon-book/Love_Coupons_loveforlove.pdf) |
| Save the Date | ✅ fertig | [products/save-the-date/Save_The_Date_loveforlove.pdf](products/save-the-date/Save_The_Date_loveforlove.pdf) |
| Invitation Suite | ✅ fertig | [products/invitation-suite/Invitation_Suite_loveforlove.pdf](products/invitation-suite/Invitation_Suite_loveforlove.pdf) |
| Wedding Day Set | ✅ fertig | [products/wedding-day-set/Wedding_Day_Set_loveforlove.pdf](products/wedding-day-set/Wedding_Day_Set_loveforlove.pdf) |
| Monogram & Crest Pack | ✅ fertig | [products/monogram-pack/Monogram_Crest_Pack_loveforlove.pdf](products/monogram-pack/Monogram_Crest_Pack_loveforlove.pdf) |
| Welcome & Guest Book Sign Set | ✅ fertig | [products/welcome-sign-set/Welcome_GuestBook_Sign_Set_loveforlove.pdf](products/welcome-sign-set/Welcome_GuestBook_Sign_Set_loveforlove.pdf) |

## Neues Produkt hinzufügen

1. Neuen Ordner unter `products/<produkt-name>/` anlegen
2. Quelldateien in `source/` ablegen
3. Fertige Verkaufsdatei direkt im Produktordner ablegen
4. Sicherstellen, dass jede Seite/Datei die Marke "Designed by loveforlove.com" trägt
5. Tabelle oben in diesem README ergänzen

## Playwright PDF Generator

Мультиязычный редактор отправляет ровно 24 карточки в `POST /api/generate-pdf`.
Flask проверяет оплату, язык, количество, порядок и ID карточек. Затем Playwright запускает
Headless Chromium, создает 24 PDF по физическим размерам из `store/cards_config.py` и
упаковывает их в `loveforlove_wedding_package.zip`.

Установка Python-зависимостей:

```bash
cd store
python -m pip install -r requirements.txt
```

Установка Chromium для Playwright на macOS/локальной машине:

```bash
python -m playwright install chromium
```

На Linux-сервере, где Playwright должен также установить системные зависимости Chromium:

```bash
python -m playwright install --with-deps chromium
```

После этого приложение запускается обычным способом, например:

```bash
gunicorn app:app
```

### Печатное качество

Playwright создает PDF с векторным текстом и CSS, поэтому для текста нет фиксированного
«DPI». Требование 300 DPI относится к растровым фонам и декоративным изображениям.
Для каждого фонового файла размером `W × H mm` исходник должен иметь минимум:

```
pixels_x = W / 25.4 * 300
pixels_y = H / 25.4 * 300
```

Фоны конкретной коллекции можно размещать по схеме:

```text
store/static/designs/<design_id>/<card_id>.webp
```

Например:

```text
store/static/designs/amalfi/02_main_invitation.webp
```

Если индивидуальный фон отсутствует, печатный Jinja-шаблон использует встроенный CSS-декор,
а не случайное или чужое изображение. Для финального коммерческого релиза все растровые
фоны должны быть подготовлены в достаточном для 300 DPI разрешении.
