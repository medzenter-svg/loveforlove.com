import os
import sys

from draft_store import draft_store_healthcheck, production_draft_storage_ready
from mailer import mail_configured
from order_store import init_order_store


DEFAULT_SECRET = "dev-secret-change-me"


def main():
    stripe_enabled = bool(os.environ.get("STRIPE_SECRET_KEY"))
    secret_key = str(os.environ.get("SECRET_KEY") or "")
    site_url = str(os.environ.get("SITE_URL") or "")

    if stripe_enabled:
        if not secret_key or secret_key == DEFAULT_SECRET:
            print("FATAL: Live payments require a non-default SECRET_KEY.", file=sys.stderr)
            return 1
        if not production_draft_storage_ready():
            print(
                "FATAL: Live payments require DATABASE_URL pointing to persistent PostgreSQL storage for editable-order drafts and paid orders.",
                file=sys.stderr,
            )
            return 1
        if not str(os.environ.get("STRIPE_WEBHOOK_SECRET") or "").strip():
            print("FATAL: Live payments require STRIPE_WEBHOOK_SECRET.", file=sys.stderr)
            return 1
        if not mail_configured():
            print("FATAL: Live payments require transactional email (SMTP_HOST and SMTP_FROM).", file=sys.stderr)
            return 1
        if not site_url.startswith("https://"):
            print("FATAL: Live payments require an HTTPS SITE_URL.", file=sys.stderr)
            return 1

    try:
        health = draft_store_healthcheck()
        init_order_store()
    except Exception as exc:
        print(f"FATAL: Persistent order/draft storage health check failed: {exc}", file=sys.stderr)
        return 1

    print(f"Draft and order storage OK ({health['mode']}).")
    if not stripe_enabled:
        print("Preview mode: PostgreSQL, Stripe webhook and transactional SMTP are recommended but not required.")
    else:
        print("Live paid fulfillment prerequisites are configured.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
