import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, abort

from products import PRODUCTS, PRODUCTS_BY_SLUG, price_display
from suite_locales import SUITE_LOCALES, LANGUAGE_NAMES, RTL_LANGUAGES

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

# In-memory order store, keyed by our own order id.
# This is intentionally still a preview-stage implementation. Before production,
# move orders to persistent storage so paid links survive application restarts.
ORDERS = {}

DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")


@app.context_processor
def inject_globals():
    return {"price_display": price_display, "live_payments": LIVE_PAYMENTS}


def get_cart():
    return session.setdefault("cart", [])


@app.route("/")
def home():
    featured = [p for p in PRODUCTS if p["category"] == "Featured Destinations"][:8]
    stationery = [p for p in PRODUCTS if p["category"] == "Stationery"][:8]
    curated = [p for p in PRODUCTS if p["category"] not in ("Featured Destinations", "Stationery")][:8]
    # The newest catalog entries automatically appear on the homepage.
    new_arrivals = list(reversed(PRODUCTS[-8:]))
    return render_template(
        "home.html",
        featured=featured,
        stationery=stationery,
        curated=curated,
        new_arrivals=new_arrivals,
    )


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


@app.route("/customize/<order_id>/<slug>")
def customize(order_id, slug):
    order = ORDERS.get(order_id)
    if not order or not order.get("paid") or slug not in order.get("slugs", []):
        abort(403)

    product = PRODUCTS_BY_SLUG.get(slug)
    if not product or not product.get("editable"):
        abort(404)

    allowed_codes = product.get("language_presets") or ["en"]
    locales = {code: SUITE_LOCALES[code] for code in allowed_codes if code in SUITE_LOCALES}
    language_names = {code: LANGUAGE_NAMES.get(code, code.upper()) for code in locales}
    rtl_languages = [code for code in RTL_LANGUAGES if code in locales]
    theme = product.get("suite_theme") or {
        "bg": "#F7F3ED",
        "paper": "#FFFDF9",
        "ink": "#181716",
        "accent": "#6F252A",
        "gold": "#B79A63",
        "line": "#DED4C7",
    }

    return render_template(
        "customize.html",
        order_id=order_id,
        product=product,
        locales=locales,
        language_names=language_names,
        rtl_languages=rtl_languages,
        theme=theme,
    )


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
        # Preview mode: simulate a paid order so purchase, editor and download
        # flows can be tested before real Stripe credentials are configured.
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
