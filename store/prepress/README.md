# Love For Love — Professional Prepress

This directory is the production layer for customer printer files. The browser editor is only for personalization and visual review. Customer press masters are generated separately and must pass QA before a product can be sold as professionally print ready.

## Production flow

1. Customer personalizes a paid collection.
2. The application creates one JSON print job containing the customer's fields, custom labels and enabled optional pieces.
3. `build_package.py` expands that job into every required professional output.
4. Each piece is opened from a dedicated Scribus `.sla` template.
5. `export_scribus.py` replaces named editable text frames and rejects text overflow.
6. The piece is exported in PDF/X-4 and PDF/X-1a.
7. Each piece is exported separately in International Metric and North American geometry.
8. `preflight.py` verifies PDF integrity, TrimBox, BleedBox, font embedding and PDF/X identification.
9. A release manifest is written only after all expected outputs pass the structural checks.
10. A product remains non-sellable until the final print package has also passed the designated commercial PDF/X validation workflow.

## Template directory contract

Each editable collection must contain prepress templates here:

```
products/<collection-slug>/prepress/
  international_metric/
    invitation.sla
    venue_address.sla
    rsvp.sla
    menu.sla
    table_number.sla
    place_card.sla
    program.sla
    thank_you.sla
    accommodation.sla
    coordinator.sla
    dress_code.sla
    envelope.sla
    envelope_liner.sla
    program_day_1.sla
    program_day_2.sla
  north_america/
    invitation.sla
    venue_address.sla
    rsvp.sla
    menu.sla
    table_number.sla
    place_card.sla
    program.sla
    thank_you.sla
    accommodation.sla
    coordinator.sla
    dress_code.sla
    envelope.sla
    envelope_liner.sla
    program_day_1.sla
    program_day_2.sla
```

The two size families are independently typeset. Do not simply scale the metric file into the North American aspect ratio.

## Editable frame naming

Scribus text frames that receive customer values must be named:

`txt__<field-key>`

Examples:

- `txt__coupleNames`
- `txt__venueAddress`
- `txt__course1`
- `txt__guestName`
- `txt__dayOneEvent1`

Translated or manually edited standard labels use:

`lbl__<label-key>`

Examples:

- `lbl__invitation`
- `lbl__menu`
- `lbl__dress_code`
- `lbl__day_one`

Frames not following these naming conventions remain locked design content.

## Scribus template rules

Every `.sla` template must already contain the final collection visual identity and production setup:

- correct trim size for that piece and size family
- correct document bleed
- color management enabled
- suitable CMYK/output-intent configuration for the professional master
- all full-bleed artwork extended through the bleed area
- critical text inside the safe area
- linked raster artwork at 300 DPI minimum at final placed size
- text, borders, ornaments and monograms kept vector wherever possible
- fonts configured for safe embedding/subsetting
- no LOVE FOR LOVE preview watermark

The customer chooses paper stock, weight and finishing with the receiving printer. The universal master must not bake in assumptions about a specific paper stock.

## Export profiles

The production package contains two formats per piece and size family:

- `PDFX4` — primary modern professional master
- `PDFX1A` — compatibility master for older commercial workflows

A fully enabled 15-piece suite therefore contains up to 60 professional PDFs:

`15 pieces × 2 size families × 2 PDF/X profiles = 60 files`

Optional pieces that the customer disables are omitted from that customer's generated package.

## Universal printer compatibility

No single fixed CMYK conversion can match every press and paper combination worldwide. The Love For Love production strategy is therefore to deliver standardized PDF/X masters with correct geometry, bleed, fonts and color management. A receiving printer may apply its exact press/paper ICC conversion without rebuilding the design.

Printer marks are not baked into the universal master. Commercial printers generally impose jobs onto their own sheets and add marks according to their finishing workflow.

## Required software on the prepress worker

The worker running `build_package.py` needs:

- Scribus with PDF/X-4 and PDF/X-1a support
- Ghostscript (`gs`)
- Poppler utilities (`pdfinfo`, `pdffonts`)
- `xvfb-run` on headless Linux systems where Scribus requires a display
- the approved fonts used by the collection
- the approved ICC profiles used by the Scribus templates

The normal Flask web process does not need to contain these large prepress dependencies. Production export should run in a dedicated worker/container.

## QA release gate

A new editable product must remain:

- `published: False`
- `professional_print_package_ready: False`

until:

- all required `.sla` templates exist
- long-name and long-address test cases do not overflow
- every expected PDF is generated
- structural preflight passes
- the final PDF/X validation workflow passes
- sample files have been visually inspected at 100% and print proofed where necessary

Only after that gate may both flags be changed to make the product sellable.
