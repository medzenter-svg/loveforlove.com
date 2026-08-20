import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import text

from draft_store import _engine, init_draft_store


EMAIL_PENDING = "pending"
EMAIL_SENDING = "sending"
EMAIL_SENT = "sent"
EMAIL_FAILED = "failed"
EMAIL_DELIVERY_LEASE_MINUTES = 10


def _now_dt():
    return datetime.now(timezone.utc)


def _now():
    return _now_dt().isoformat()


def init_order_store():
    init_draft_store()
    statements = [
        """
        CREATE TABLE IF NOT EXISTS paid_orders (
            order_id TEXT PRIMARY KEY,
            stripe_session_id TEXT UNIQUE,
            customer_email TEXT NOT NULL,
            slugs_json TEXT NOT NULL,
            paid_at TEXT NOT NULL,
            access_email_status TEXT NOT NULL DEFAULT 'pending',
            access_email_attempts INTEGER NOT NULL DEFAULT 0,
            access_email_sent_at TEXT,
            access_email_last_error TEXT,
            updated_at TEXT NOT NULL
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_paid_orders_email
        ON paid_orders(customer_email)
        """,
    ]
    with _engine().begin() as db:
        for statement in statements:
            db.execute(text(statement))


def record_paid_order(order_id, stripe_session_id, customer_email, slugs):
    init_order_store()
    order_id = str(order_id)
    stripe_session_id = str(stripe_session_id or "") or None
    customer_email = str(customer_email).strip().lower()
    slugs_json = json.dumps(sorted(set(slugs)), separators=(",", ":"))
    now = _now()

    with _engine().begin() as db:
        row = db.execute(
            text("SELECT order_id FROM paid_orders WHERE order_id = :order_id"),
            {"order_id": order_id},
        ).mappings().first()
        if row:
            db.execute(
                text(
                    "UPDATE paid_orders SET stripe_session_id = :stripe_session_id, "
                    "customer_email = :customer_email, slugs_json = :slugs_json, updated_at = :updated_at "
                    "WHERE order_id = :order_id"
                ),
                {
                    "stripe_session_id": stripe_session_id,
                    "customer_email": customer_email,
                    "slugs_json": slugs_json,
                    "updated_at": now,
                    "order_id": order_id,
                },
            )
        else:
            db.execute(
                text(
                    "INSERT INTO paid_orders(order_id, stripe_session_id, customer_email, slugs_json, paid_at, updated_at) "
                    "VALUES (:order_id, :stripe_session_id, :customer_email, :slugs_json, :paid_at, :updated_at)"
                ),
                {
                    "order_id": order_id,
                    "stripe_session_id": stripe_session_id,
                    "customer_email": customer_email,
                    "slugs_json": slugs_json,
                    "paid_at": now,
                    "updated_at": now,
                },
            )
    return get_paid_order(order_id)


def get_paid_order(order_id):
    init_order_store()
    with _engine().connect() as db:
        row = db.execute(
            text("SELECT * FROM paid_orders WHERE order_id = :order_id"),
            {"order_id": str(order_id)},
        ).mappings().first()
    if row is None:
        return None
    result = dict(row)
    result["slugs"] = json.loads(result.pop("slugs_json"))
    return result


def begin_access_email_delivery(order_id):
    """Atomically reserve one email delivery attempt.

    Pending and failed deliveries can be reserved immediately. A delivery left
    in `sending` for more than EMAIL_DELIVERY_LEASE_MINUTES is treated as an
    abandoned worker reservation and may be retried. `sent` is never retried.
    """
    init_order_store()
    now_dt = _now_dt()
    now = now_dt.isoformat()
    stale_before = (now_dt - timedelta(minutes=EMAIL_DELIVERY_LEASE_MINUTES)).isoformat()

    with _engine().begin() as db:
        result = db.execute(
            text(
                "UPDATE paid_orders SET access_email_status = :sending, "
                "access_email_attempts = access_email_attempts + 1, updated_at = :updated_at "
                "WHERE order_id = :order_id AND ("
                "access_email_status IN (:pending, :failed) "
                "OR (access_email_status = :sending_status AND updated_at < :stale_before)"
                ")"
            ),
            {
                "sending": EMAIL_SENDING,
                "sending_status": EMAIL_SENDING,
                "pending": EMAIL_PENDING,
                "failed": EMAIL_FAILED,
                "updated_at": now,
                "stale_before": stale_before,
                "order_id": str(order_id),
            },
        )
        return result.rowcount == 1


def mark_access_email_sent(order_id):
    init_order_store()
    now = _now()
    with _engine().begin() as db:
        db.execute(
            text(
                "UPDATE paid_orders SET access_email_status = :sent, access_email_sent_at = :sent_at, "
                "access_email_last_error = NULL, updated_at = :updated_at WHERE order_id = :order_id"
            ),
            {
                "sent": EMAIL_SENT,
                "sent_at": now,
                "updated_at": now,
                "order_id": str(order_id),
            },
        )


def mark_access_email_failed(order_id, error):
    init_order_store()
    message = str(error or "")[:2000]
    with _engine().begin() as db:
        db.execute(
            text(
                "UPDATE paid_orders SET access_email_status = :failed, access_email_last_error = :error, "
                "updated_at = :updated_at WHERE order_id = :order_id"
            ),
            {
                "failed": EMAIL_FAILED,
                "error": message,
                "updated_at": _now(),
                "order_id": str(order_id),
            },
        )
