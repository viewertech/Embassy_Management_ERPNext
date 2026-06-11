from __future__ import annotations

import hashlib
import hmac
import json
import time
from decimal import Decimal, ROUND_HALF_UP

import frappe
import requests
from frappe import _

from embassy_management.api.finance import _create_sales_invoice


STRIPE_API_BASE = "https://api.stripe.com/v1"
STRIPE_API_VERSION = "2026-02-25.clover"
ZERO_DECIMAL_CURRENCIES = {
    "BIF",
    "CLP",
    "DJF",
    "GNF",
    "JPY",
    "KMF",
    "KRW",
    "MGA",
    "PYG",
    "RWF",
    "UGX",
    "VND",
    "VUV",
    "XAF",
    "XOF",
    "XPF",
}


def is_stripe_enabled():
    if not frappe.db.exists("DocType", "Embassy Settings"):
        return False
    settings = frappe.get_single("Embassy Settings")
    return bool(settings.get("stripe_enabled"))


@frappe.whitelist()
def create_checkout_session(application):
    settings = _get_settings()
    if not settings.get("stripe_enabled"):
        frappe.throw(_("Stripe Checkout is not enabled in Embassy Settings."))

    secret_key = _get_secret(settings, "stripe_secret_key")
    if not secret_key:
        frappe.throw(_("Please configure the Stripe Secret Key in Embassy Settings."))

    app = frappe.get_doc("Consular Application", application)
    app.check_permission("read")
    if app.application_status in {"Draft", "Rejected", "Cancelled", "Completed", "Collected / Dispatched"}:
        frappe.throw(_("Submit an active application before starting Stripe payment."))
    if app.payment_status in {"Not Required", "Payment Confirmed", "Refunded"}:
        frappe.throw(_("This application does not have an outstanding Stripe payment."))

    invoice = _create_sales_invoice(app.name, ignore_permissions=True)
    invoice_name = invoice.name
    service = frappe.get_doc("Consular Service", app.service)
    amount = app.total_fee or service.default_fee or 0
    currency = (app.currency or service.currency or settings.default_currency or "USD").upper()
    unit_amount = _to_minor_units(amount, currency)
    if unit_amount <= 0:
        frappe.throw(_("This application has no payable Stripe amount."))

    payload = _checkout_payload(settings, app, service, invoice_name, amount, currency, unit_amount)
    response = _stripe_post(
        "/checkout/sessions",
        secret_key,
        payload,
        idempotency_key=f"ems-checkout-{app.name}-{frappe.generate_hash(length=12)}",
    )

    session_id = response.get("id")
    checkout_url = response.get("url")
    _store_checkout_reference(app, invoice_name, amount, currency, session_id, checkout_url)

    return {
        "checkout_url": checkout_url,
        "session_id": session_id,
        "application": app.name,
        "sales_invoice": invoice_name,
    }


@frappe.whitelist(allow_guest=True)
def stripe_webhook():
    settings = _get_settings()
    if not settings.get("stripe_enabled"):
        frappe.local.response.http_status_code = 400
        return {"ok": False, "error": "Stripe is not enabled"}

    payload = frappe.request.get_data(as_text=True)
    signature = frappe.request.headers.get("Stripe-Signature")
    webhook_secret = _get_secret(settings, "stripe_webhook_secret")

    if not webhook_secret:
        frappe.local.response.http_status_code = 400
        return {"ok": False, "error": "Stripe webhook secret is not configured"}

    if not _verify_signature(payload, signature, webhook_secret):
        frappe.local.response.http_status_code = 400
        return {"ok": False, "error": "Invalid Stripe signature"}

    try:
        event = json.loads(payload)
    except json.JSONDecodeError:
        frappe.local.response.http_status_code = 400
        return {"ok": False, "error": "Invalid JSON"}

    event_type = event.get("type")
    obj = (event.get("data") or {}).get("object") or {}
    if event_type == "checkout.session.completed":
        _handle_checkout_completed(event, obj)
    elif event_type == "checkout.session.expired":
        _handle_checkout_expired(event, obj)
    elif event_type == "payment_intent.payment_failed":
        _handle_payment_failed(event, obj)

    return {"ok": True}


def _get_settings():
    if not frappe.db.exists("DocType", "Embassy Settings"):
        frappe.throw(_("Embassy Settings is not installed."))
    return frappe.get_single("Embassy Settings")


def _get_secret(settings, fieldname):
    try:
        return settings.get_password(fieldname)
    except Exception:
        return settings.get(fieldname)


def _checkout_payload(settings, app, service, invoice_name, amount, currency, unit_amount):
    success_url = settings.get("stripe_success_url") or frappe.utils.get_url(
        "/embassy/dashboard?payment=success&session_id={CHECKOUT_SESSION_ID}"
    )
    cancel_url = settings.get("stripe_cancel_url") or frappe.utils.get_url(
        f"/embassy/dashboard?payment=cancelled&application={app.name}"
    )
    customer_email = frappe.db.get_value("Embassy Applicant Profile", app.applicant, "email")
    description = f"{service.service_name} - {app.application_number or app.name}"

    payload = {
        "mode": "payment",
        "client_reference_id": app.name,
        "success_url": success_url,
        "cancel_url": cancel_url,
        "line_items[0][quantity]": 1,
        "line_items[0][price_data][currency]": currency.lower(),
        "line_items[0][price_data][unit_amount]": unit_amount,
        "line_items[0][price_data][product_data][name]": service.service_name,
        "line_items[0][price_data][product_data][description]": description,
        "metadata[application]": app.name,
        "metadata[application_number]": app.application_number or app.name,
        "metadata[sales_invoice]": invoice_name,
        "payment_intent_data[metadata][application]": app.name,
        "payment_intent_data[metadata][sales_invoice]": invoice_name,
    }
    if customer_email:
        payload["customer_email"] = customer_email
    if settings.get("stripe_mode"):
        payload["metadata[stripe_mode]"] = settings.get("stripe_mode")
    if amount:
        payload["metadata[amount]"] = str(amount)
    return payload


def _stripe_post(path, secret_key, data, idempotency_key=None):
    headers = {"Stripe-Version": STRIPE_API_VERSION}
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    response = requests.post(
        f"{STRIPE_API_BASE}{path}",
        auth=(secret_key, ""),
        data=data,
        headers=headers,
        timeout=30,
    )
    try:
        payload = response.json()
    except ValueError:
        payload = {}
    if response.status_code >= 400:
        message = (payload.get("error") or {}).get("message") or response.text
        frappe.throw(_("Stripe request failed: {0}").format(message))
    return payload


def _to_minor_units(amount, currency):
    value = Decimal(str(amount or 0))
    multiplier = Decimal("1") if currency.upper() in ZERO_DECIMAL_CURRENCIES else Decimal("100")
    return int((value * multiplier).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _store_checkout_reference(app, invoice_name, amount, currency, session_id, checkout_url):
    frappe.db.set_value(
        "Consular Application",
        app.name,
        {
            "payment_status": "Payment Pending",
            "stripe_payment_status": "Pending",
            "stripe_checkout_session_id": session_id,
            "stripe_checkout_url": checkout_url,
        },
        update_modified=False,
    )

    review_name = frappe.db.get_value(
        "Consular Payment Review",
        {"stripe_checkout_session_id": session_id},
        "name",
    )
    review = frappe.get_doc("Consular Payment Review", review_name) if review_name else frappe.new_doc("Consular Payment Review")
    review.application = app.name
    review.sales_invoice = invoice_name
    review.amount = amount
    review.currency = currency
    review.review_status = "Pending"
    review.review_notes = _("Stripe Checkout session created.")
    review.stripe_checkout_session_id = session_id
    review.stripe_checkout_url = checkout_url
    if review.name:
        review.save(ignore_permissions=True)
    else:
        review.insert(ignore_permissions=True)


def _verify_signature(payload, header, secret):
    if not header:
        return False
    parts = {}
    for item in header.split(","):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        parts.setdefault(key, []).append(value)
    timestamp = (parts.get("t") or [None])[0]
    signatures = parts.get("v1") or []
    if not timestamp or not signatures:
        return False
    try:
        timestamp_int = int(timestamp)
    except ValueError:
        return False
    if abs(time.time() - timestamp_int) > 300:
        return False
    signed_payload = f"{timestamp}.{payload}".encode()
    expected = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(expected, signature) for signature in signatures)


def _handle_checkout_completed(event, session):
    application = (session.get("metadata") or {}).get("application") or session.get("client_reference_id")
    if not application or not frappe.db.exists("Consular Application", application):
        return

    payment_intent = session.get("payment_intent")
    app = frappe.get_doc("Consular Application", application)
    values = {
        "payment_status": "Payment Confirmed",
        "stripe_payment_status": "Paid",
        "stripe_checkout_session_id": session.get("id"),
        "stripe_payment_intent": payment_intent,
    }
    if app.application_status == "Payment Pending":
        values["application_status"] = "Payment Confirmed"
    frappe.db.set_value("Consular Application", app.name, values, update_modified=False)
    _update_review_from_event(app, event, session, "Confirmed", payment_intent)


def _handle_checkout_expired(event, session):
    application = (session.get("metadata") or {}).get("application") or session.get("client_reference_id")
    if not application or not frappe.db.exists("Consular Application", application):
        return
    frappe.db.set_value(
        "Consular Application",
        application,
        {"stripe_payment_status": "Expired", "stripe_checkout_session_id": session.get("id")},
        update_modified=False,
    )
    _update_review_from_event(frappe.get_doc("Consular Application", application), event, session, "Rejected", None)


def _handle_payment_failed(event, payment_intent):
    application = (payment_intent.get("metadata") or {}).get("application")
    if not application or not frappe.db.exists("Consular Application", application):
        return
    frappe.db.set_value(
        "Consular Application",
        application,
        {
            "payment_status": "Failed",
            "stripe_payment_status": "Failed",
            "stripe_payment_intent": payment_intent.get("id"),
        },
        update_modified=False,
    )


def _update_review_from_event(app, event, session, status, payment_intent):
    review_name = frappe.db.get_value(
        "Consular Payment Review",
        {"stripe_checkout_session_id": session.get("id")},
        "name",
    )
    review = frappe.get_doc("Consular Payment Review", review_name) if review_name else frappe.new_doc("Consular Payment Review")
    review.application = app.name
    review.sales_invoice = app.sales_invoice
    review.amount = app.total_fee
    review.currency = app.currency
    review.review_status = status
    review.reviewed_by = frappe.session.user
    review.reviewed_on = frappe.utils.now()
    review.review_notes = _("Stripe webhook processed: {0}").format(event.get("type"))
    review.stripe_checkout_session_id = session.get("id")
    review.stripe_payment_intent = payment_intent
    review.stripe_event_id = event.get("id")
    review.stripe_event_type = event.get("type")
    review.stripe_webhook_received_on = frappe.utils.now()
    if review.name:
        review.save(ignore_permissions=True)
    else:
        review.insert(ignore_permissions=True)
