# loveforlove.com

Premium editable digital stationery for weddings and other celebrations.

## Current product status

The repository contains legacy PDF products and the new editable wedding-suite system. Legacy wedding PDFs must **not** be treated as professionally print-ready merely because a PDF file exists. Wedding products remain gated until the new prepress workflow, professional PDF/X export and QA are complete.

The editable complete wedding suite currently contains 8 core pieces plus 7 optional pieces, including accommodation, coordinator contact, Dress Code, matching envelope/liner and two-day wedding program cards.

## Paid editable orders

Editable products are designed to remain editable after purchase:

1. The customer pays for the product.
2. Stripe confirms the paid Checkout session through the signed webhook.
3. The paid order is stored persistently with its order number, purchase email and purchased product slugs.
4. A transactional email is sent with the order number and a protected **Open your design** link. The editable source is not attached to the email.
5. Access is bound to the paid order number and purchase email.
6. A new browser/device must verify the same purchase email.
7. The customer can edit the same purchased copy repeatedly.
8. Drafts are saved by `order_id + product slug`.
9. The latest 20 revisions are retained so an earlier version can be restored.
10. A stale browser cannot silently overwrite a newer saved revision from another device.

The purchase email is not stored in clear text inside the access URL. The URL contains a signed, per-order HMAC verifier instead. Once the paid order has been persisted, long-term access is verified from the persistent order record rather than requiring a new Stripe API lookup on every visit.

## Automatic order access email

`store/payments.py` handles signed Stripe webhook fulfillment. `store/order_store.py` stores paid orders and email-delivery state so normal duplicate Stripe events do not send duplicate access emails. A failed delivery is marked retryable.

The customer email contains:

- order number
- names of purchased products
- protected access link
- instruction to verify the same checkout email on a new browser/device
- reminder that the purchased copy can be reopened and edited later

No editable master file is attached to the email.

## Persistent storage

Local development may use SQLite. Production with real Stripe payments requires PostgreSQL through `DATABASE_URL`.

Required production environment variables:

```text
SECRET_KEY=<strong unique secret>
STRIPE_SECRET_KEY=<Stripe secret key>
STRIPE_WEBHOOK_SECRET=<Stripe webhook signing secret>
DATABASE_URL=<persistent PostgreSQL URL>
SITE_URL=https://<production-domain>
SMTP_HOST=<transactional SMTP host>
SMTP_PORT=587
SMTP_FROM=<orders sender address>
SMTP_USERNAME=<if required>
SMTP_PASSWORD=<if required>
SMTP_USE_STARTTLS=true
```

`store/startup_check.py` runs before Gunicorn. If live payments are enabled while the secret key, persistent PostgreSQL storage, signed Stripe webhook, HTTPS site URL or transactional email are not configured, the web process refuses to start. This prevents selling an editable product whose saved customer changes or access delivery are not reliable.

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
  wsgi.py
  draft_store.py
  order_store.py
  mailer.py
  payments.py
  persistent_access.py
  products.py
  prepress/
  static/
  templates/
  tests/
```
