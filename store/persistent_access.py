import hmac

from flask import abort

from order_store import get_paid_order


def install_persistent_paid_access(store_app):
    """Replace repeated Stripe lookups with verified persistent paid-order access.

    The original Stripe-backed checker remains the fallback for the short window
    before a paid Checkout session has been persisted by fulfillment.
    """
    original_paid_access = store_app.paid_access

    def persistent_paid_access(access_token, slug=None):
        payload = store_app.read_access_token(access_token)
        if payload.get("dev_paid"):
            return original_paid_access(access_token, slug)

        order_id = str(payload.get("order_id") or "")
        order = get_paid_order(order_id)
        if order is None:
            return original_paid_access(access_token, slug)

        token_session_id = str(payload.get("stripe_session_id") or "")
        stored_session_id = str(order.get("stripe_session_id") or "")
        token_email_hash = str(payload.get("customer_email_hash") or "")
        stored_email_hash = store_app.email_digest(order["customer_email"], order_id)
        token_slugs = set(payload.get("slugs") or [])
        stored_slugs = set(order.get("slugs") or [])

        paid = (
            bool(token_session_id)
            and hmac.compare_digest(token_session_id, stored_session_id)
            and hmac.compare_digest(token_email_hash, stored_email_hash)
            and token_slugs == stored_slugs
        )
        if not paid:
            abort(403)
        if slug and slug not in stored_slugs:
            abort(403)
        return payload

    store_app.paid_access = persistent_paid_access
    return persistent_paid_access
