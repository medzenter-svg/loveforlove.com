import os
import secrets

from flask import Flask, abort, redirect, render_template, request, send_from_directory, session, url_for
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from i18n import LANGUAGES, translate
from products import COLLECTIONS, PRODUCTS, price_display

try:
    import stripe
except ImportError:  # pragma: no cover - deployment dependency guard
    stripe = None


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "products"))

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("SITE_URL", "").startswith("https://"),
)

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
SITE_URL = os.environ.get("SITE_URL", "http://localhost:5000").rstrip("/")
LIVE_PAYMENTS = bool(stripe and STRIPE_SECRET_KEY)
DOWNLOAD_LINK_MAX_AGE = int(os.environ.get("DOWNLOAD_LINK_MAX_AGE", 60 * 60 * 24 * 7))

if LIVE_PAYMENTS:
    stripe.api_key = STRIPE_SECRET_KEY

signer = URLSafeTimedSerializer(app.secret_key, salt="loveforlove-downloads")


def product_file_exists(product, filename):
    expected = os.path.realpath(os.path.join(PRODUCTS_DIR, product["slug"], filename))
    root = os.path.realpath(os.path.join(PRODUCTS_DIR, product["slug"]))
    return expected.startswith(root + os.sep) and os.path.isfile(expected)


def verified_catalog():
    return [p for p in PRODUCTS if p.get("sale_ready") is True and p["files"] and all(product_file_exists(p, f) for f in p["files"])]


def catalog_by_slug():
    return {p["slug"]: p for p in verified_catalog()}


@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.context_processor
def inject_globals():
    language = session.get("language", "en")
    return {
        "price_display": price_display,
        "live_payments": LIVE_PAYMENTS,
        "cart_count": len(session.get("cart", [])),
        "language": language,
        "languages": LANGUAGES,
        "page_direction": "rtl" if language == "he" else "ltr",
        "t": lambda key: translate(language, key),
    }


def get_cart():
    return session.setdefault("cart", [])


@app.route("/")
def home():
    products = verified_catalog()
    featured = [p for p in products if p["category"] == "Collections"][:8]
    stationery = [p for p in products if p["category"] == "Stationery"][:8]
    curated = [p for p in products if p["category"] not in ("Collections", "Stationery")][:8]
    return render_template("home.html", featured=featured, stationery=stationery, curated=curated, collections=COLLECTIONS)


@app.post("/language/<code>")
def set_language(code):
    if code not in LANGUAGES:
        abort(404)
    session["language"] = code
    target = request.form.get("next", "/")
    if not target.startswith("/") or target.startswith("//"):
        target = "/"
    return redirect(target)


@app.route("/shop")
def shop():
    category = request.args.get("category")
    products = verified_catalog()
    if category:
        products = [p for p in products if p["category"] == category]
    categories = sorted({p["category"] for p in verified_catalog()})
    return render_template("shop.html", products=products, categories=categories, active_category=category)


@app.route("/product/<slug>")
def product_detail(slug):
    product = catalog_by_slug().get(slug)
    if not product:
        abort(404)
    return render_template("product.html", product=product)


@app.post("/cart/add/<slug>")
def cart_add(slug):
    if slug not in catalog_by_slug():
        abort(404)
    cart = get_cart()
    if slug not in cart:
        cart.append(slug)
    session["cart"] = cart
    session.modified = True
    return redirect(url_for("cart_view"))


@app.post("/cart/remove/<slug>")
def cart_remove(slug):
    session["cart"] = [item for item in get_cart() if item != slug]
    session.modified = True
    return redirect(url_for("cart_view"))


@app.route("/cart")
def cart_view():
    available = catalog_by_slug()
    items = [available[s] for s in get_cart() if s in available]
    total = sum(p["price"] for p in items)
    return render_template("cart.html", items=items, total=total)


@app.post("/checkout")
def checkout():
    available = catalog_by_slug()
    items = [available[s] for s in get_cart() if s in available]
    if not items:
        return redirect(url_for("cart_view"))

    slugs = [p["slug"] for p in items]
    if not LIVE_PAYMENTS:
        token = signer.dumps({"slugs": slugs, "mode": "preview"})
        session["cart"] = []
        return redirect(url_for("success", preview_token=token))

    line_items = [
        {
            "price_data": {
                "currency": "eur",
                "product_data": {"name": p["name"]},
                "unit_amount": p["price"],
            },
            "quantity": 1,
        }
        for p in items
    ]
    checkout_session = stripe.checkout.Session.create(
        mode="payment",
        line_items=line_items,
        success_url=f"{SITE_URL}/success?stripe_session={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{SITE_URL}/cancel",
        metadata={"product_slugs": ",".join(slugs)},
    )
    session["cart"] = []
    return redirect(checkout_session.url, code=303)


@app.route("/success")
def success():
    available = catalog_by_slug()
    if LIVE_PAYMENTS:
        stripe_session_id = request.args.get("stripe_session")
        if not stripe_session_id:
            abort(400)
        try:
            checkout_session = stripe.checkout.Session.retrieve(stripe_session_id)
        except Exception:
            abort(400)
        if checkout_session.payment_status != "paid":
            return render_template("cancel.html", reason="payment_incomplete"), 402
        slugs = [s for s in checkout_session.metadata.get("product_slugs", "").split(",") if s in available]
        token = signer.dumps({"slugs": slugs, "stripe_session": stripe_session_id})
    else:
        token = request.args.get("preview_token")
        try:
            payload = signer.loads(token, max_age=300)
            slugs = [s for s in payload.get("slugs", []) if s in available]
        except (BadSignature, SignatureExpired, TypeError):
            abort(403)

    if not slugs:
        abort(404)
    items = [available[s] for s in slugs]
    return render_template("success.html", items=items, download_token=token, dev_mode=not LIVE_PAYMENTS)


@app.route("/cancel")
def cancel():
    return render_template("cancel.html", reason="cancelled")


@app.route("/download/<token>/<slug>/<path:filename>")
def download(token, slug, filename):
    try:
        payload = signer.loads(token, max_age=DOWNLOAD_LINK_MAX_AGE)
    except SignatureExpired:
        abort(410)
    except (BadSignature, TypeError):
        abort(403)

    product = catalog_by_slug().get(slug)
    if not product or slug not in payload.get("slugs", []) or filename not in product["files"]:
        abort(403)
    if not product_file_exists(product, filename):
        abort(404)
    return send_from_directory(os.path.join(PRODUCTS_DIR, slug), filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
