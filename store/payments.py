from flask import Blueprint, jsonify, request, url_for

from mailer import mail_configured, send_order_access_email
from order_store import (
    begin_access_email_delivery,
    mark_access_email_failed,
    mark_access_email_sent,
    record_paid_order,
)


payments_bp = Blueprint("payments", __name__)


def _value(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def fulfill_paid_session(checkout_session, require_email_delivery=True):
    """Persist a paid Stripe Checkout order and send its access email once."""
    import app as store_app

    if _value(checkout_session, "payment_status") != "paid":
        return None

    metadata = _value(checkout_session, "metadata") or {}
    order_id = str(_value(metadata, "order_id") or "")
    slugs = [slug for slug in str(_value(metadata, "slugs") or "").split(",") if slug]
    stripe_session_id = str(_value(checkout_session, "id") or "")
    customer_email = store_app.stripe_session_email(checkout_session)

    if not order_id or not stripe_session_id or not store_app.valid_customer_email(customer_email) or not slugs:
        raise RuntimeError("Paid Stripe session is missing order ID, products, session ID or customer email")

    unknown = [slug for slug in slugs if slug not in store_app.PRODUCTS_BY_SLUG]
    if unknown:
        raise RuntimeError("Paid Stripe session contains unknown products: " + ", ".join(unknown))

    record_paid_order(order_id, stripe_session_id, customer_email, slugs)
    access_token = store_app.make_access_token(
        order_id,
        slugs,
        customer_email,
        stripe_session_id=stripe_session_id,
    )
    success_path = url_for("success", access_token=access_token)
    access_path = url_for("order_access", access_token=access_token, next=success_path)
    access_url = store_app.SITE_URL.rstrip("/") + access_path

    email_sent = False
    if begin_access_email_delivery(order_id):
        try:
            if not mail_configured():
                raise RuntimeError("Transactional email is not configured")
            product_names = [store_app.PRODUCTS_BY_SLUG[slug]["name"] for slug in slugs]
            send_order_access_email(
                customer_email,
                order_id,
                access_url,
                product_names,
            )
        except Exception as exc:
            mark_access_email_failed(order_id, exc)
            if require_email_delivery:
                raise
        else:
            mark_access_email_sent(order_id)
            email_sent = True

    return {
        "order_id": order_id,
        "slugs": slugs,
        "customer_email": customer_email,
        "access_token": access_token,
        "access_url": access_url,
        "email_sent": email_sent,
    }


@payments_bp.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    import app as store_app

    if not store_app.LIVE_PAYMENTS:
        return jsonify({"ok": False, "error": "Live payments are disabled."}), 404

    webhook_secret = str(store_app.os.environ.get("STRIPE_WEBHOOK_SECRET") or "").strip()
    if not webhook_secret:
        return jsonify({"ok": False, "error": "Stripe webhook is not configured."}), 503

    signature = request.headers.get("Stripe-Signature", "")
    try:
        event = store_app.stripe.Webhook.construct_event(
            request.get_data(cache=False),
            signature,
            webhook_secret,
        )
    except Exception:
        return jsonify({"ok": False, "error": "Invalid Stripe webhook signature."}), 400

    event_type = _value(event, "type")
    if event_type in {"checkout.session.completed", "checkout.session.async_payment_succeeded"}:
        data = _value(event, "data") or {}
        checkout_session = _value(data, "object")
        if checkout_session is not None and _value(checkout_session, "payment_status") == "paid":
            try:
                fulfill_paid_session(checkout_session, require_email_delivery=True)
            except Exception:
                # Non-2xx makes Stripe retry the webhook. Email delivery state is
                # persisted, so a successful earlier send will not be duplicated.
                return jsonify({"ok": False, "error": "Order fulfillment failed."}), 500

    return jsonify({"ok": True})
