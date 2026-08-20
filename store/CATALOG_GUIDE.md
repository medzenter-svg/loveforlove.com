# Love For Love — Catalog workflow

This file defines the operating rule for adding new products without exposing master artwork.

## Three-file-layer rule

Every design has three separate layers:

1. **Master artwork** — the editable original/source files. These stay off the public website and are never placed in `store/static`.
2. **Store preview** — a reduced preview image placed in `store/static/products/<slug>/`. The storefront adds the LOVE FOR LOVE watermark overlay.
3. **Customer delivery** — the clean print-ready PDF/ZIP/JPG/PNG listed in the product's `files` field and served only through the paid-download route.

## Coordinated-suite standard

A full wedding collection must look like one design family, not unrelated cards. The collection owns one shared visual system: palette, typography, borders, ornaments, spacing and illustration/photography treatment. Every piece inherits that system.

The standard full suite contains:

1. Invitation
2. Venue & full address card
3. RSVP card
4. Menu with first course, second course, third course and dessert
5. Table number / table name
6. Guest place card
7. Wedding program
8. Thank-you card

Optional matching extensions can add Save the Date, Welcome Sign, Seating Chart, Bar Menu, Gift Table Sign or other wedding-day pieces without changing the core design language.

## Editable-suite standard

When a product is marked `editable`, the buyer receives access to the paid-only online suite editor. The design itself remains locked and coordinated while the buyer can change:

- couple names
- wedding date and time
- venue name
- full venue address
- RSVP deadline and contact details
- all four menu courses and descriptions
- table number or table name
- guest name
- program times
- thank-you message
- every standard label and heading

Language presets are conveniences, not restrictions. Presets may be provided for common languages, while every label remains manually editable so the buyer can use any language or custom wording.

## Add a product

1. Choose a unique lowercase slug, for example `amalfi-gold-invitation`.
2. Create `store/static/products/<slug>/cover.webp` (or the existing supported image format).
3. Put only the clean customer delivery file in the protected download location used by the app. Never put the master source there.
4. Add one item to `PRODUCTS` in `store/products.py` with:
   - `slug`
   - `name`
   - `category`
   - `price` (USD cents)
   - `description`
   - `cover`
   - `files`
5. For a coordinated editable collection also add:
   - `editable: True`
   - `suite_items`
   - `suite_theme`
   - `language_presets`
   - `custom_language: True`
6. Put new products at the end of `PRODUCTS`. The homepage automatically treats the latest entries as **New Arrivals**.
7. Open the product page and verify preview, name, price, description, cart, checkout, editor access and delivery filename before publishing.

## Storefront rules

- Public product images are previews only.
- The LOVE FOR LOVE watermark must remain subtle but cross the design area so it cannot be removed by simply cropping an edge.
- Do not publish full-resolution editable originals as public static files.
- Do not advertise a language, currency, file type, personalization option or included item unless it is actually delivered.
- A coordinated suite may be sold both as separate pieces and as a higher-value bundle, but each listing must state exactly what is included.
- New premium wedding collections should be built as families first; individual products may then be derived from that family.

## Daily expansion pattern

Prefer adding products in coordinated families so one new visual concept can create several sellable products without creating visual chaos. A family can be sold as the complete suite and, where useful, as separate invitation, menu, signage or seating products.

Before a collection is published, verify that all pieces use the same palette, type hierarchy, border language and decorative treatment and that the editable text does not collide with the design at realistic long-name and long-address lengths.
