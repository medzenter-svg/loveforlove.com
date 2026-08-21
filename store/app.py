import os
from flask import Flask, render_template, request, abort

from products import PRODUCTS, PRODUCTS_BY_SLUG

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "test-editor-only")


@app.context_processor
def inject_globals():
    return {"test_mode": True}


@app.route("/")
def home():
    return render_template("home.html", product=PRODUCTS[0])


@app.route("/shop")
def shop():
    return render_template("shop.html", products=PRODUCTS)


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
    return render_template("editor.html", product=product)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
