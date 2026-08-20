import os
import sys

from draft_store import draft_store_healthcheck, production_draft_storage_ready


DEFAULT_SECRET = "dev-secret-change-me"


def main():
    stripe_enabled = bool(os.environ.get("STRIPE_SECRET_KEY"))
    secret_key = str(os.environ.get("SECRET_KEY") or "")

    if stripe_enabled:
        if not secret_key or secret_key == DEFAULT_SECRET:
            print("FATAL: Live payments require a non-default SECRET_KEY.", file=sys.stderr)
            return 1
        if not production_draft_storage_ready():
            print(
                "FATAL: Live payments require DATABASE_URL pointing to persistent PostgreSQL storage for editable-order drafts.",
                file=sys.stderr,
            )
            return 1

    try:
        health = draft_store_healthcheck()
    except Exception as exc:
        print(f"FATAL: Draft storage health check failed: {exc}", file=sys.stderr)
        return 1

    print(f"Draft storage OK ({health['mode']}).")
    if not stripe_enabled:
        print("Preview mode: persistent PostgreSQL is recommended but not required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
