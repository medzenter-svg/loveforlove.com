# Love For Love — Catalog workflow

This file defines the operating rule for adding new products without exposing master artwork.

## Brand scope

Love For Love is a premium stationery brand for meaningful personal celebrations. Weddings remain the core category, while the catalog expands carefully into adjacent occasions that fit the same emotional and visual positioning:

1. Weddings
2. Wedding anniversaries and vow renewals
3. Milestone adult birthdays
4. Engagement parties and bridal events
5. Selected elegant family celebrations

Do not dilute the brand with unrelated generic party templates. Each new occasion must receive a coordinated design family and only become publicly purchasable when the real customer deliverables are ready.

## Three-file-layer rule

Every design has three separate layers:

1. **Master artwork** — the editable original/source files. These stay off the public website and are never placed in `store/static`.
2. **Store preview** — a reduced preview image placed in `store/static/products/<slug>/`. The storefront adds the LOVE FOR LOVE watermark overlay.
3. **Customer delivery** — clean professional print files served only through the paid-download route.

## Coordinated-suite standard

A complete collection must look like one design family, not unrelated cards. The collection owns one shared visual system: palette, typography, borders, ornaments, spacing, monogram language and illustration/photography treatment. Every piece inherits that system.

The wedding core contains:

1. Invitation
2. Venue & full address card
3. RSVP card
4. Menu with first course, second course, third course and dessert
5. Table number / table name
6. Guest place card
7. Wedding program
8. Thank-you card

The premium optional layer contains:

9. Guest accommodation / hotel card
10. Wedding coordinator / guest-contact card
11. Dress Code card
12. Matching envelope design
13. Matching envelope liner

Other matching extensions can add Save the Date, Welcome Sign, Seating Chart, Bar Menu, Gift Table Sign, transport information, weekend itinerary or other event-specific pieces without changing the design language.

Optional pieces must be switchable off in the editor so the buyer prints only what is relevant to the event.

## Editable-suite standard

When a product is marked `editable`, the buyer receives access to the paid-only online editor. The design itself remains locked and coordinated while the buyer can change event content.

For weddings, editable content includes:

- couple names
- date and time
- venue name and full address
- RSVP deadline and contact details
- all four menu courses and descriptions
- table number or table name
- guest name
- program times
- thank-you message
- hotel name, address, check-in/check-out, booking and transfer details
- coordinator name, role, phone, messenger and email
- Dress Code wording
- envelope recipient and return address
- monogram / initials
- every standard label and heading

Language presets are conveniences, not restrictions. Presets may be provided for common languages, while every label remains manually editable so the buyer can use any language or custom wording.

## Other occasion suites

Anniversary, vow-renewal and milestone-birthday collections reuse the same technical system but replace wedding-specific language with occasion-specific wording.

- Anniversary / vow renewal: invitation, venue card, RSVP, dinner menu, seating, program, accommodation, coordinator, Dress Code, thank-you, envelope and liner.
- Milestone birthday: invitation, venue card, RSVP, dinner/menu card, table card, guest place card, schedule, Dress Code, hotel/travel information when relevant, coordinator/contact card, thank-you, envelope and liner.

Do not force wedding-specific fields into non-wedding products. Reuse the architecture, not inappropriate wording.

## Worldwide professional print standard

The online editor is for personalization and visual review. **A browser Print/Save PDF is not the customer press master.**

Every printable piece must be generated as its own professional production file. A complete thirteen-piece collection therefore produces thirteen separate print pieces, not one long browser PDF.

### Required professional exports

Each piece is delivered in two professional compatibility formats:

1. **PDF/X-4** — primary master for modern commercial and digital print workflows.
2. **PDF/X-1a** — compatibility master for older print workflows that do not accept PDF/X-4.

This is deliberately broader than offering one generic PDF. It allows the receiving printer to choose the workflow it supports without rebuilding the design.

### Required production properties

- 300 DPI minimum for raster artwork at final placed size
- text, borders, ornaments and monograms kept vector wherever possible
- fonts embedded; selected display lettering may be converted to outlines in the final press export
- defined TrimBox and BleedBox
- critical text kept at least 5 mm / 0.2 in inside the trim edge
- ICC color-managed production PDF with an output intent
- print shop may perform the final conversion to its own press/paper ICC condition without altering the layout
- no watermark on purchased professional files
- paper stock, paper weight, finish, foil, embossing and printing method remain the buyer/printer's choice

### Two worldwide size families

Every coordinated design is typeset separately in two size families; one final PDF must never simply be scaled into the other because line breaks, safe areas and envelope proportions differ.

**International Metric**

- A6 invitation
- A6 venue/address card
- A7 RSVP
- DL menu
- A6 table number
- 85 × 55 mm place card
- A5 program
- A6 thank-you
- A6 accommodation card
- A7 coordinator card
- A6 Dress Code card
- C6 envelope and matching liner
- 3 mm bleed

**North America**

- 5 × 7 in invitation
- 4 × 6 in venue/address card
- 3.5 × 5 in RSVP
- 4 × 9 in menu
- 5 × 7 in table number
- 3.5 × 2 in place card
- 5 × 7 in program
- 5 × 3.5 in thank-you
- 5 × 7 in accommodation card
- 5 × 3.5 in coordinator card
- 5 × 7 in Dress Code card
- A7 envelope and matching liner
- 0.125 in bleed

### What “works with printers worldwide” means

No responsible seller can guarantee that one single CMYK conversion or one marks preset matches every printing press and every paper stock in the world. Different printers may request a specific ICC profile or their own crop-mark policy. Love For Love solves this by providing standardized PDF/X masters, correct page boxes, bleed, vector construction, embedded fonts and a print-specification sheet. The receiving printer can then apply its exact machine/paper conversion without redesigning the customer's artwork.

## Add a product

1. Choose a unique lowercase slug, for example `amalfi-gold-invitation`.
2. Create `store/static/products/<slug>/cover.webp` (or the existing supported preview image format).
3. Never expose editable master artwork publicly.
4. Add one item to `PRODUCTS` in `store/products.py` with:
   - `slug`
   - `name`
   - `category`
   - `occasion`
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
   - professional print profile
6. Put new published products at the end of `PRODUCTS`. The homepage automatically treats the latest entries as **New Arrivals**.
7. Keep unfinished products with `published: False` until the actual PDF/X print package exists and passes QA.
8. Verify preview, name, price, description, cart, checkout, editor access, optional-piece toggles, every exported size, every PDF/X file and every delivery filename before publishing.

## Storefront rules

- Public product images are previews only.
- The LOVE FOR LOVE watermark must remain subtle but cross the design area so it cannot be removed by simply cropping an edge.
- Do not publish full-resolution editable originals as public static files.
- Do not advertise a language, currency, file type, personalization option or included item unless it is actually delivered.
- Do not use the phrase “professional print ready” until the PDF/X exports for that product have passed preflight.
- A coordinated suite may be sold both as separate pieces and as a higher-value bundle, but each listing must state exactly what is included.
- Planned or in-development occasion categories may be shown as roadmap sections, but must not appear to be purchasable until at least one completed product exists.

## Daily expansion pattern

Prefer adding products in coordinated families so one new visual concept can create several sellable products without visual chaos. A family can be sold as the complete suite and, where useful, as separate invitation, menu, signage, seating or envelope products.

Before a collection is published, verify that all pieces use the same palette, type hierarchy, border language and decorative treatment; all editable fields work; long names and addresses do not collide with the design; optional pieces can be excluded cleanly; both metric and North American versions are correctly reflowed; and the actual PDF/X print files match every storefront claim.
