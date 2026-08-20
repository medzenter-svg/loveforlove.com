# Love For Love — Catalog workflow

This file defines the operating rule for adding new products without exposing master artwork.

## Three-file-layer rule

Every design has three separate layers:

1. **Master artwork** — the editable original/source files. These stay off the public website and are never placed in `store/static`.
2. **Store preview** — a reduced preview image placed in `store/static/products/<slug>/`. The storefront adds the LOVE FOR LOVE watermark overlay.
3. **Customer delivery** — the clean print-ready PDF/ZIP/JPG/PNG listed in the product's `files` field and served only through the paid-download route.

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
5. Put new products at the end of `PRODUCTS`. The homepage automatically treats the latest entries as **New Arrivals**.
6. Open the product page and verify preview, name, price, description, cart, checkout and delivery filename before publishing.

## Storefront rules

- Public product images are previews only.
- The LOVE FOR LOVE watermark must remain subtle but cross the design area so it cannot be removed by simply cropping an edge.
- Do not publish full-resolution editable originals as public static files.
- Do not advertise a language, currency, file type, personalization option or included item unless it is actually delivered.
- A coordinated suite may be sold both as separate pieces and as a higher-value bundle, but each listing must state exactly what is included.

## Daily expansion pattern

Prefer adding products in coordinated families:

- Invitation
- Save the Date
- RSVP
- Menu
- Table Number
- Place Card
- Ceremony Program
- Welcome Sign
- Thank You Card

This lets the catalog grow every day while preserving a coherent premium visual identity.
