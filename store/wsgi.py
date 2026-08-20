import app as store_app
from payments import payments_bp
from persistent_access import install_persistent_paid_access


install_persistent_paid_access(store_app)
app = store_app.app

if "payments" not in app.blueprints:
    app.register_blueprint(payments_bp)
