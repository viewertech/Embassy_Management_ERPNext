from __future__ import annotations

from decimal import Decimal, InvalidOperation

import frappe


def get_field(doc, fieldname):
    if isinstance(doc, dict):
        return doc.get(fieldname)
    return getattr(doc, fieldname, None)


def clean(value):
    if value in (None, ""):
        return None
    return str(value)


def join_title(parts):
    return " | ".join(part for part in (clean(part) for part in parts) if part)


def link_title(doctype, name, title_field=None):
    if not name:
        return None

    if doctype == "User":
        return frappe.db.get_value("User", name, "full_name") or name

    if title_field:
        return frappe.db.get_value(doctype, name, title_field) or name

    try:
        meta = frappe.get_meta(doctype)
        if meta.title_field:
            return frappe.db.get_value(doctype, name, meta.title_field) or name
    except Exception:
        pass

    return name


def format_amount(amount, currency=None):
    if amount in (None, ""):
        return None
    try:
        value = Decimal(str(amount))
        text = f"{value:,.2f}".rstrip("0").rstrip(".")
    except (InvalidOperation, ValueError):
        text = str(amount)
    return f"{currency} {text}" if currency else text


def application_label(application):
    if not application:
        return None

    row = frappe.db.get_value(
        "Consular Application",
        application,
        ["application_number", "applicant", "service"],
        as_dict=True,
    )
    if not row:
        return application

    return join_title(
        [
            row.application_number or application,
            link_title("Embassy Applicant Profile", row.applicant, "full_name"),
            link_title("Consular Service", row.service, "service_name"),
        ]
    )


def build_fee_rule_title(doc):
    nationality = get_field(doc, "nationality")
    residence_country = get_field(doc, "residence_country")
    residence = f"Resident {residence_country}" if residence_country else None

    return join_title(
        [
            link_title("Consular Service", get_field(doc, "service"), "service_name") or "Fee Rule",
            get_field(doc, "visa_type"),
            get_field(doc, "entry_type"),
            get_field(doc, "processing_type"),
            nationality,
            residence,
            format_amount(get_field(doc, "amount"), get_field(doc, "currency")),
        ]
    )


def build_fee_waiver_title(doc):
    return join_title(
        [
            "Fee Waiver",
            application_label(get_field(doc, "application")),
            get_field(doc, "waiver_type"),
            format_amount(get_field(doc, "amount"), get_field(doc, "currency")),
        ]
    )


def build_payment_review_title(doc):
    return join_title(
        [
            "Payment Review",
            application_label(get_field(doc, "application")),
            get_field(doc, "review_status"),
            format_amount(get_field(doc, "amount"), get_field(doc, "currency")),
        ]
    )


def build_service_details_title(doc, label, fieldnames):
    return join_title(
        [
            label,
            application_label(get_field(doc, "consular_application")),
            *[get_field(doc, fieldname) for fieldname in fieldnames],
        ]
    )
