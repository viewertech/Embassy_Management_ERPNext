from __future__ import annotations

import frappe
from frappe import _


@frappe.whitelist()
def create_sales_invoice(application):
    app = frappe.get_doc("Consular Application", application)
    app.check_permission("write")
    if app.sales_invoice:
        return frappe.get_doc("Sales Invoice", app.sales_invoice).as_dict()
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
    invoice.insert()
    app.sales_invoice = invoice.name
    app.payment_status = "Payment Pending"
    app.save(ignore_permissions=True)
    return invoice.as_dict()


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
