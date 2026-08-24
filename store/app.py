import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, abort, jsonify

from products import PRODUCTS, PRODUCTS_BY_SLUG, price_display
from cards_config import CARDS_CONFIG, CARDS_BY_ID, SUPPORTED_LANGUAGES, printable_dimensions, EXPECTED_CARD_COUNT

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
SITE_URL = os.environ.get("SITE_URL", "http://localhost:5000")

if STRIPE_AVAILABLE and STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY
    LIVE_PAYMENTS = True
else:
    LIVE_PAYMENTS = False

ORDERS = {}
DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
PREVIEW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "preview")


@app.context_processor
def inject_globals():
    return {"price_display": price_display, "live_payments": LIVE_PAYMENTS}


def get_cart():
    return session.setdefault("cart", [])


def order_allows_editor(order_id, slug):
    if not order_id:
        return False
    order = ORDERS.get(order_id)
    return bool(order and order.get("paid") and slug in order.get("slugs", []))


def render_stationery_editor(product, order_id=None):
    is_paid = order_allows_editor(order_id, product["slug"])
    return render_template(
        "editor.html",
        product=product,
        cards_config=CARDS_CONFIG,
        supported_languages=SUPPORTED_LANGUAGES,
        expected_card_count=EXPECTED_CARD_COUNT,
        is_paid=is_paid,
        order_id=order_id or "",
    )


@app.route("/")
def home():
    featured = [p for p in PRODUCTS if p["category"] == "Featured Destinations"][:8]
    stationery = [p for p in PRODUCTS if p["category"] == "Stationery"][:8]
    curated = [p for p in PRODUCTS if p["category"] not in ("Featured Destinations", "Stationery")][:8]
    return render_template("home.html", featured=featured, stationery=stationery, curated=curated)


@app.route("/shop")
def shop():
    category = request.args.get("category")
    products = PRODUCTS
    if category:
        products = [p for p in PRODUCTS if p["category"] == category]
    categories = sorted(set(p["category"] for p in PRODUCTS))
    return render_template("shop.html", products=products, categories=categories, active_category=category)


@app.route("/product/<slug>")
def product_detail(slug):
    product = PRODUCTS_BY_SLUG.get(slug)
    if not product:
        abort(404)
    return render_template("product.html", product=product)


@app.route("/test-editor/<slug>")
def test_editor(slug):
    product = PRODUCTS_BY_SLUG.get(slug)
    if not product:
        abort(404)
    return render_stationery_editor(product, request.args.get("order_id"))


@app.route("/amalfi-editor")
def amalfi_editor():
    product = PRODUCTS_BY_SLUG.get("amalfi-wedding-suite")
    if not product:
        abort(404)
    return render_stationery_editor(product, request.args.get("order_id"))


@app.route("/api/stationery/config")
def stationery_config_api():
    return jsonify({
        "languages": SUPPORTED_LANGUAGES,
        "expected_card_count": EXPECTED_CARD_COUNT,
        "cards": CARDS_CONFIG,
    })


@app.route("/api/stationery/payload", methods=["POST"])
def stationery_payload_api():
    payload = request.get_json(silent=True) or {}
    language = payload.get("language")
    order_id = payload.get("order_id")
    slug = payload.get("product_slug", "amalfi-wedding-suite")

    if language not in SUPPORTED_LANGUAGES:
        return jsonify({"error": "unsupported_language"}), 400
    if not order_allows_editor(order_id, slug):
        return jsonify({"error": "payment_required"}), 403

    incoming_cards = payload.get("cards")
    if not isinstance(incoming_cards, list):
        return jsonify({"error": "cards_must_be_a_list"}), 400
    if len(incoming_cards) != EXPECTED_CARD_COUNT:
        return jsonify({
            "error": "invalid_card_count",
            "expected": EXPECTED_CARD_COUNT,
            "received": len(incoming_cards),
        }), 400

    submitted_ids = [submitted.get("id") for submitted in incoming_cards]
    expected_ids = [card["id"] for card in CARDS_CONFIG]
    if submitted_ids != expected_ids:
        return jsonify({"error": "invalid_card_order_or_ids"}), 400

    normalized = []
    for submitted in incoming_cards:
        card_id = submitted["id"]
        config = CARDS_BY_ID[card_id]

        allowed_fields = set(config.get("fields", []))
        values = submitted.get("values") or {}
        clean_values = {key: str(value) for key, value in values.items() if key in allowed_fields}

        requested_view = submitted.get("view")
        valid_views = config.get("views", [])
        normalized.append({
            "id": card_id,
            "view": requested_view if requested_view in valid_views else valid_views[0],
            "values": clean_values,
            "print": printable_dimensions(config),
        })

    return jsonify({
        "ok": True,
        "language": language,
        "product_slug": slug,
        "card_count": len(normalized),
        "cards": normalized,
    })


@app.route("/amalfi-preview")
def amalfi_preview():
    return render_template("amalfi_preview.html")


@app.route("/preview-assets/<path:filename>")
def preview_asset(filename):
    return send_from_directory(PREVIEW_DIR, filename)


@app.route("/cart/add/<slug>", methods=["POST"])
def cart_add(slug):
    if slug not in PRODUCTS_BY_SLUG:
        abort(404)
    cart = get_cart()
    if slug not in cart:
        cart.append(slug)
    session["cart"] = cart
    session.modified = True
    return redirect(url_for("cart_view"))


@app.route("/cart/remove/<slug>", methods=["POST"])
def cart_remove(slug):
    cart = get_cart()
    if slug in cart:
        cart.remove(slug)
    session["cart"] = cart
    session.modified = True
    return redirect(url_for("cart_view"))


@app.route("/cart")
def cart_view():
    cart = get_cart()
    items = [PRODUCTS_BY_SLUG[s] for s in cart if s in PRODUCTS_BY_SLUG]
    total = sum(p["price"] for p in items)
    return render_template("cart.html", items=items, total=total)


@app.route("/checkout", methods=["POST"])
def checkout():
    cart = get_cart()
    items = [PRODUCTS_BY_SLUG[s] for s in cart if s in PRODUCTS_BY_SLUG]
    if not items:
        return redirect(url_for("cart_view"))

    order_id = uuid.uuid4().hex
    ORDERS[order_id] = {"slugs": [p["slug"] for p in items], "paid": False}

    if LIVE_PAYMENTS:
        line_items = [{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": p["name"]},
                "unit_amount": p["price"],
            },
            "quantity": 1,
        } for p in items]
        checkout_session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            success_url=f"{SITE_URL}/success?order_id={order_id}&stripe_session={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{SITE_URL}/cancel",
            metadata={"order_id": order_id},
        )
        ORDERS[order_id]["stripe_session_id"] = checkout_session.id
        session["cart"] = []
        return redirect(checkout_session.url, code=303)
    else:
        ORDERS[order_id]["paid"] = True
        session["cart"] = []
        return redirect(url_for("success", order_id=order_id))


@app.route("/success")
def success():
    order_id = request.args.get("order_id")
    order = ORDERS.get(order_id)
    if not order:
        abort(404)

    if LIVE_PAYMENTS and not order["paid"]:
        stripe_session_id = order.get("stripe_session_id")
        try:
            s = stripe.checkout.Session.retrieve(stripe_session_id)
            if s.payment_status == "paid":
                order["paid"] = True
        except Exception:
            pass

    if not order["paid"]:
        return render_template("cancel.html", reason="payment_incomplete")

    items = [PRODUCTS_BY_SLUG[s] for s in order["slugs"] if s in PRODUCTS_BY_SLUG]
    return render_template("success.html", items=items, order_id=order_id, dev_mode=not LIVE_PAYMENTS)


@app.route("/cancel")
def cancel():
    return render_template("cancel.html", reason="cancelled")


@app.route("/download/<order_id>/<slug>/<path:filename>")
def download(order_id, slug, filename):
    order = ORDERS.get(order_id)
    if not order or not order.get("paid") or slug not in order["slugs"]:
        abort(403)
    product = PRODUCTS_BY_SLUG.get(slug)
    if not product or filename not in product["files"]:
        abort(404)
    return send_from_directory(DOWNLOADS_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
