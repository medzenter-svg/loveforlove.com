from app import app
from payments import payments_bp


if "payments" not in app.blueprints:
    app.register_blueprint(payments_bp)
