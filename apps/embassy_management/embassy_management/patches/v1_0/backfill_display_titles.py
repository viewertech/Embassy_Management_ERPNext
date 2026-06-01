import frappe

from embassy_management.embassy_management.doctype.application_uploaded_document.application_uploaded_document import (
    build_document_title,
)
from embassy_management.embassy_management.doctype.appointment_slot.appointment_slot import (
    build_slot_label,
)


def execute():
    doctypes = (
        "appointment_slot",
        "application_uploaded_document",
        "application_document_requirement",
        "consular_application",
        "embassy_appointment",
    )
    for doctype in doctypes:
        frappe.reload_doc("embassy_management", "doctype", doctype)

    for row in frappe.get_all(
        "Appointment Slot",
        fields=[
            "name",
            "service",
            "appointment_service_type",
            "location",
            "slot_date",
            "from_time",
            "to_time",
        ],
    ):
        label = build_slot_label(row)
        if label:
            frappe.db.set_value("Appointment Slot", row.name, "slot_label", label, update_modified=False)

    for row in frappe.get_all(
        "Application Uploaded Document",
        fields=["name", "application", "requirement", "document_category", "status"],
    ):
        title = build_document_title(row)
        if title:
            frappe.db.set_value("Application Uploaded Document", row.name, "document_title", title, update_modified=False)
