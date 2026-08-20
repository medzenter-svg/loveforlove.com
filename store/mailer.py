import os
import smtplib
import ssl
from email.message import EmailMessage


class MailConfigurationError(RuntimeError):
    pass


def mail_configured():
    required = ["SMTP_HOST", "SMTP_FROM"]
    return all(str(os.environ.get(name) or "").strip() for name in required)


def _smtp_settings():
    host = str(os.environ.get("SMTP_HOST") or "").strip()
    sender = str(os.environ.get("SMTP_FROM") or "").strip()
    if not host or not sender:
        raise MailConfigurationError("SMTP_HOST and SMTP_FROM are required")

    port = int(os.environ.get("SMTP_PORT") or "587")
    username = str(os.environ.get("SMTP_USERNAME") or "").strip()
    password = str(os.environ.get("SMTP_PASSWORD") or "")
    use_ssl = str(os.environ.get("SMTP_USE_SSL") or "").lower() in {"1", "true", "yes"}
    use_starttls = str(os.environ.get("SMTP_USE_STARTTLS") or "true").lower() in {"1", "true", "yes"}
    timeout = float(os.environ.get("SMTP_TIMEOUT_SECONDS") or "15")

    if username and not password:
        raise MailConfigurationError("SMTP_PASSWORD is required when SMTP_USERNAME is set")
    if use_ssl and use_starttls:
        use_starttls = False

    return {
        "host": host,
        "port": port,
        "sender": sender,
        "username": username,
        "password": password,
        "use_ssl": use_ssl,
        "use_starttls": use_starttls,
        "timeout": timeout,
    }


def build_order_access_message(customer_email, order_id, access_url, product_names):
    product_lines = "\n".join(f"• {name}" for name in product_names) or "• Your purchased design"

    message = EmailMessage()
    message["Subject"] = f"Your Love For Love design — order {order_id}"
    message["To"] = customer_email
    message.set_content(
        "Thank you for your purchase from Love For Love.\n\n"
        f"Order: {order_id}\n\n"
        "Your purchased editable design is ready:\n"
        f"{product_lines}\n\n"
        "Open your design:\n"
        f"{access_url}\n\n"
        "For security, a new browser or device will ask you to enter the same email address used during checkout. "
        "You can return to this link later and continue editing your saved copy.\n\n"
        "Keep this email for future access to your purchased design.\n\n"
        "Love For Love\n"
        "loveforlove.com"
    )
    return message


def send_order_access_email(customer_email, order_id, access_url, product_names):
    settings = _smtp_settings()
    message = build_order_access_message(customer_email, order_id, access_url, product_names)
    message["From"] = settings["sender"]

    if settings["use_ssl"]:
        client = smtplib.SMTP_SSL(
            settings["host"],
            settings["port"],
            timeout=settings["timeout"],
            context=ssl.create_default_context(),
        )
    else:
        client = smtplib.SMTP(settings["host"], settings["port"], timeout=settings["timeout"])

    try:
        client.ehlo()
        if settings["use_starttls"]:
            client.starttls(context=ssl.create_default_context())
            client.ehlo()
        if settings["username"]:
            client.login(settings["username"], settings["password"])
        client.send_message(message)
    finally:
        try:
            client.quit()
        except Exception:
            pass
