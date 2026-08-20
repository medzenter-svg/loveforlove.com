# loveforlove.com

Premium editable digital stationery for weddings and other celebrations.

## Current product status

The repository contains legacy PDF products and the new editable wedding-suite system. Legacy wedding PDFs must **not** be treated as professionally print-ready merely because a PDF file exists. Wedding products remain gated until the new prepress workflow, professional PDF/X export and QA are complete.

The editable complete wedding suite currently contains 8 core pieces plus 7 optional pieces, including accommodation, coordinator contact, Dress Code, matching envelope/liner and two-day wedding program cards.

## Paid editable orders

Editable products are designed to remain editable after purchase:

1. The customer pays for the product.
2. Access is bound to the paid order number and purchase email.
3. A new browser/device must verify the same purchase email.
4. The customer can edit the same purchased copy repeatedly.
5. Drafts are saved by `order_id + product slug`.
6. The latest 20 revisions are retained so an earlier version can be restored.
7. A stale browser cannot silently overwrite a newer saved revision from another device.

The purchase email is not stored in clear text inside the access URL. The URL contains a signed, per-order HMAC verifier instead.

## Persistent draft storage

Local development may use SQLite. Production with real Stripe payments requires PostgreSQL through `DATABASE_URL`.

Required production environment variables:

```text
SECRET_KEY=<strong unique secret>
STRIPE_SECRET_KEY=<Stripe secret key>
DATABASE_URL=<persistent PostgreSQL URL>
SITE_URL=https://<production-domain>
```

`store/startup_check.py` runs before Gunicorn. If live payments are enabled while `SECRET_KEY` is still the development default, PostgreSQL is missing, or the draft database cannot be reached, the web process refuses to start. This prevents selling an editable product whose saved customer changes could disappear after a server restart.

For local development only, `DRAFT_DB_PATH` can point to a SQLite file.

## Professional print workflow

The browser editor is the customer editing surface; it is not the final prepress engine. Professional printer files are produced through the separate Scribus/PDF/X workflow under `store/prepress/`.

The wedding suite remains blocked from sale until the professional package is generated and validated. See `store/prepress/README.md` and `store/CATALOG_GUIDE.md` for the production rules.

## Repository structure

```text
products/
  <product-slug>/
    ... product assets ...

store/
  app.py
  draft_store.py
  products.py
  prepress/
  static/
  templates/
  tests/
```
