import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, abort, jsonify
from itsdangerous import URLSafeSerializer, BadSignature

from products import (
    PRODUCTS_BY_SLUG,
    PUBLISHED_PRODUCTS,
    OCCASION_ROADMAP,
    is_sellable_product,
    price_display,
)
from suite_locales import SUITE_LOCALES, LANGUAGE_NAMES, RTL_LANGUAGES
from suite_optional_locales import OPTIONAL_SUITE_LOCALES
from suite_weekend_locales import WEEKEND_SUITE_LOCALES
from prepress.job import PrintJobValidationError, normalize_print_job
from print_package import package_summary

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

ORDER_SIGNER = URLSafeSerializer(app.secret_key, salt="loveforlove-paid-access-v1")
PRODUCTS_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "products"))


@app.context_processor
def inject_globals():
    return {"price_display": price_display, "live_payments": LIVE_PAYMENTS}


def get_cart():
    return session.setdefault("cart", [])


def make_access_token(order_id, slugs, stripe_session_id=None, dev_paid=False):
    return ORDER_SIGNER.dumps({
        "order_id": order_id,
        "slugs": list(slugs),
        "stripe_session_id": stripe_session_id,
        "dev_paid": bool(dev_paid),
    })


def read_access_token(access_token):
    try:
        payload = ORDER_SIGNER.loads(access_token)
    except BadSignature:
        abort(403)
    if not isinstance(payload, dict) or not isinstance(payload.get("slugs"), list):
        abort(403)
    return payload


def paid_access(access_token, slug=None):
    payload = read_access_token(access_token)

    if payload.get("dev_paid"):
        paid = not LIVE_PAYMENTS
    else:
        stripe_session_id = payload.get("stripe_session_id")
        paid = False
        if LIVE_PAYMENTS and stripe_session_id:
            try:
                checkout_session = stripe.checkout.Session.retrieve(stripe_session_id)
                paid = checkout_session.payment_status == "paid"
            except Exception:
                paid = False

    if not paid:
        abort(403)
    if slug and slug not in payload.get("slugs", []):
        abort(403)
    return payload


@app.route("/")
def home():
    featured = [p for p in PUBLISHED_PRODUCTS if p["category"] == "Featured Destinations"][:8]
    stationery = [p for p in PUBLISHED_PRODUCTS if p["category"] == "Stationery"][:8]
    curated = [p for p in PUBLISHED_PRODUCTS if p["category"] not in ("Featured Destinations", "Stationery")][:8]
    new_arrivals = list(reversed(PUBLISHED_PRODUCTS[-8:]))
    return render_template(
        "home.html",
        featured=featured,
        stationery=stationery,
        curated=curated,
        new_arrivals=new_arrivals,
        occasion_roadmap=OCCASION_ROADMAP,
    )


@app.route("/shop")
def shop():
    category = request.args.get("category")
    occasion = request.args.get("occasion")
    products = PUBLISHED_PRODUCTS
    if category:
        products = [p for p in products if p["category"] == category]
    if occasion:
        products = [p for p in products if p.get("occasion") == occasion]
    categories = sorted(set(p["category"] for p in PUBLISHED_PRODUCTS))
    occasions = sorted(set(p.get("occasion") for p in PUBLISHED_PRODUCTS if p.get("occasion")))
    return render_template(
        "shop.html",
        products=products,
        categories=categories,
        occasions=occasions,
        active_category=category,
        active_occasion=occasion,
    )


@app.route("/product/<slug>")
def product_detail(slug):
    product = PRODUCTS_BY_SLUG.get(slug)
    if not product or not is_sellable_product(product):
        abort(404)
    return render_template("product.html", product=product)


@app.route("/customize/<access_token>/<slug>")
def customize(access_token, slug):
    payload = paid_access(access_token, slug)
    product = PRODUCTS_BY_SLUG.get(slug)
    if not product or not product.get("editable"):
        abort(404)

    allowed_codes = product.get("language_presets") or ["en"]
    locales = {}
    for code in allowed_codes:
        if code not in SUITE_LOCALES:
            continue
        merged = dict(SUITE_LOCALES[code])
        merged.update(OPTIONAL_SUITE_LOCALES.get(code, {}))
        merged.update(WEEKEND_SUITE_LOCALES.get(code, {}))
        locales[code] = merged

    language_names = {code: LANGUAGE_NAMES.get(code, code.upper()) for code in locales}
    rtl_languages = [code for code in RTL_LANGUAGES if code in locales]
    theme = product.get("suite_theme") or {
        "bg": "#F7F3ED", "paper": "#FFFDF9", "ink": "#181716",
        "accent": "#6F252A", "gold": "#B79A63", "line": "#DED4C7",
    }

    return render_template(
        "customize.html",
        access_token=access_token,
        order_id=payload.get("order_id", "order"),
        product=product,
        locales=locales,
        language_names=language_names,
        rtl_languages=rtl_languages,
        theme=theme,
    )


@app.route("/customize/<access_token>/<slug>/print-job/validate", methods=["POST"])
def validate_print_job(access_token, slug):
    paid_access(access_token, slug)
    product = PRODUCTS_BY_SLUG.get(slug)
    if not product or not product.get("editable"):
        abort(404)

    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"ok": False, "error": "Print job must be JSON."}), 400

    try:
        job = normalize_print_job(slug, payload)
    except PrintJobValidationError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    summary = package_summary(slug, job["enabled_optional"])
    return jsonify({
        "ok": True,
        "collection": slug,
        "language": job["language"],
        "enabled_optional": job["enabled_optional"],
        "printable_pieces": summary["printable_pieces"],
        "professional_pdf_files": summary["professional_pdf_files"],
        "files_per_piece": summary["files_per_piece"],
        "professional_print_package_ready": bool(product.get("professional_print_package_ready", False)),
    })


@app.route("/cart/add/<slug>", methods=["POST"])
def cart_add(slug):
    product = PRODUCTS_BY_SLUG.get(slug)
    if not product or not is_sellable_product(product):
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
    sellable_slugs = {p["slug"] for p in PUBLISHED_PRODUCTS}
    cart = [slug for slug in get_cart() if slug in sellable_slugs]
    session["cart"] = cart
    items = [PRODUCTS_BY_SLUG[s] for s in cart]
    total = sum(p["price"] for p in items)
    return render_template("cart.html", items=items, total=total)


@app.route("/checkout", methods=["POST"])
def checkout():
    sellable_slugs = {p["slug"] for p in PUBLISHED_PRODUCTS}
    cart = [slug for slug in get_cart() if slug in sellable_slugs]
    items = [PRODUCTS_BY_SLUG[s] for s in cart]
    if not items:
        return redirect(url_for("cart_view"))

    order_id = uuid.uuid4().hex
    slugs = [p["slug"] for p in items]

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
            success_url=f"{SITE_URL}/success?stripe_session={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{SITE_URL}/cancel",
            metadata={"order_id": order_id, "slugs": ",".join(slugs)},
        )
        session["cart"] = []
        return redirect(checkout_session.url, code=303)

    access_token = make_access_token(order_id, slugs, dev_paid=True)
    session["cart"] = []
    return redirect(url_for("success", access_token=access_token))


@app.route("/success")
def success():
    access_token = request.args.get("access_token")

    if access_token:
        payload = paid_access(access_token)
    else:
        stripe_session_id = request.args.get("stripe_session")
        if not LIVE_PAYMENTS or not stripe_session_id:
            abort(404)
        try:
            checkout_session = stripe.checkout.Session.retrieve(stripe_session_id)
        except Exception:
            return render_template("cancel.html", reason="payment_incomplete")
        if checkout_session.payment_status != "paid":
            return render_template("cancel.html", reason="payment_incomplete")

        metadata = checkout_session.metadata or {}
        slugs = [slug for slug in (metadata.get("slugs") or "").split(",") if slug]
        order_id = metadata.get("order_id") or uuid.uuid4().hex
        access_token = make_access_token(order_id, slugs, stripe_session_id=checkout_session.id)
        payload = {"order_id": order_id, "slugs": slugs}

    items = [PRODUCTS_BY_SLUG[s] for s in payload.get("slugs", []) if s in PRODUCTS_BY_SLUG]
    return render_template("success.html", items=items, access_token=access_token, dev_mode=not LIVE_PAYMENTS)


@app.route("/cancel")
def cancel():
    return render_template("cancel.html", reason="cancelled")


@app.route("/download/<access_token>/<slug>/<path:filename>")
def download(access_token, slug, filename):
    paid_access(access_token, slug)
    product = PRODUCTS_BY_SLUG.get(slug)
    if not product or filename not in product.get("files", []):
        abort(404)

    product_dir = os.path.join(PRODUCTS_DIR, slug)
    file_path = os.path.join(product_dir, filename)
    if not os.path.isfile(file_path):
        abort(404)
    return send_from_directory(product_dir, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
