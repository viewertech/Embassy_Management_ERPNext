from __future__ import annotations

import frappe
from frappe import _


@frappe.whitelist()
def create_sales_invoice(application):
    invoice = _create_sales_invoice(application)
    return invoice.as_dict()


def _create_sales_invoice(application, ignore_permissions=False):
    app = frappe.get_doc("Consular Application", application)
    app.check_permission("read" if ignore_permissions else "write")
    if app.sales_invoice:
        return frappe.get_doc("Sales Invoice", app.sales_invoice)

    _ensure_billing_party(app)
    service = frappe.get_doc("Consular Service", app.service)
    if not service.fee_item:
        frappe.throw(_("Please configure a Fee Item for this service."))
    if not app.customer:
        frappe.throw(_("Please link the application to an ERPNext Customer before invoicing."))
    invoice = frappe.new_doc("Sales Invoice")
    invoice.customer = app.customer
    invoice.currency = app.currency or service.currency
    invoice.append("items", {
        "item_code": service.fee_item,
        "qty": 1,
        "rate": app.total_fee or service.default_fee or 0,
        "description": service.service_name,
    })
    invoice.insert(ignore_permissions=ignore_permissions)
    app.sales_invoice = invoice.name
    app.payment_status = "Payment Pending"
    app.save(ignore_permissions=True)
    return invoice


def _ensure_billing_party(app):
    if app.customer:
        return
    if not app.applicant:
        frappe.throw(_("Please link the application to an applicant before invoicing."))

    profile = frappe.get_doc("Embassy Applicant Profile", app.applicant)
    if profile.customer:
        app.customer = profile.customer
        if profile.contact and not app.contact:
            app.contact = profile.contact
        app.save(ignore_permissions=True)
        return

    customer_group = _first_existing("Customer Group", "Individual", "All Customer Groups")
    territory = _first_existing("Territory", "All Territories")
    if not customer_group or not territory:
        frappe.throw(_("Please configure ERPNext Customer Group and Territory before creating invoices."))

    customer = frappe.new_doc("Customer")
    customer.customer_name = profile.full_name or profile.email or profile.name
    customer.customer_type = "Individual"
    customer.customer_group = customer_group
    customer.territory = territory
    customer.insert(ignore_permissions=True)

    profile.customer = customer.name
    if not profile.contact:
        profile.contact = _get_or_create_contact(profile, customer.name)
    profile.save(ignore_permissions=True)

    app.customer = customer.name
    app.contact = profile.contact
    app.save(ignore_permissions=True)


def _get_or_create_contact(profile, customer):
    contact_name = frappe.db.get_value("Contact Email", {"email_id": profile.email}, "parent") if profile.email else None
    contact = frappe.get_doc("Contact", contact_name) if contact_name else frappe.new_doc("Contact")

    if contact.is_new():
        name_parts = (profile.full_name or profile.email or profile.name).split(" ", 1)
        contact.first_name = name_parts[0]
        contact.last_name = name_parts[1] if len(name_parts) > 1 else None
        if profile.email:
            contact.append("email_ids", {"email_id": profile.email, "is_primary": 1})
        if profile.mobile_no:
            contact.append("phone_nos", {"phone": profile.mobile_no, "is_primary_phone": 1})

    if not any(link.link_doctype == "Customer" and link.link_name == customer for link in contact.links):
        contact.append("links", {"link_doctype": "Customer", "link_name": customer})

    if contact.is_new():
        contact.insert(ignore_permissions=True)
    else:
        contact.save(ignore_permissions=True)
    return contact.name


def _first_existing(doctype, *names):
    for name in names:
        if frappe.db.exists(doctype, name):
            return name
    return frappe.db.get_value(doctype, {}, "name")


@frappe.whitelist()
def mark_payment_confirmed(application, payment_entry=None, notes=None):
    app = frappe.get_doc("Consular Application", application)
    app.check_permission("write")
    app.payment_entry = payment_entry
    app.payment_status = "Payment Confirmed"
    if app.application_status == "Payment Pending":
        app.application_status = "Payment Confirmed"
    app.save()
    review = frappe.new_doc("Consular Payment Review")
    review.application = app.name
    review.sales_invoice = app.sales_invoice
    review.payment_entry = payment_entry
    review.amount = app.total_fee
    review.currency = app.currency
    review.review_status = "Confirmed"
    review.review_notes = notes
    review.reviewed_by = frappe.session.user
    review.reviewed_on = frappe.utils.now()
    review.insert()
    return review.as_dict()
