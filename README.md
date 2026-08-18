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

## Neues Produkt hinzufügen

1. Neuen Ordner unter `products/<produkt-name>/` anlegen
2. Quelldateien in `source/` ablegen
3. Fertige Verkaufsdatei direkt im Produktordner ablegen
4. Sicherstellen, dass jede Seite/Datei die Marke "Designed by loveforlove.com" trägt
5. Tabelle oben in diesem README ergänzen
