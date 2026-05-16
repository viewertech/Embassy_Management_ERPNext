from __future__ import annotations

import frappe

from embassy_management.setup import import_sample_data


SAMPLE_SERVICE_CODES = ("GEN-VISA", "GEN-PASSPORT", "GEN-CARD", "GEN-ATTEST")
SAMPLE_LOCATION = "Generic Consular Counter"


def load_sample_data():
    clear_sample_data()
    import_sample_data()
    frappe.db.commit()
    return "EMSDEMO sample data loaded."


def clear_sample_data():
    for doctype, filters in (
        ("Application Uploaded Document", {"application": ["like", "GEN-%"]}),
        ("Application Document Requirement", {"application": ["like", "GEN-%"]}),
        ("Embassy Appointment", {"service": ["in", SAMPLE_SERVICE_CODES]}),
        ("Appointment Slot", {"service": ["in", SAMPLE_SERVICE_CODES]}),
        ("Consular Payment Review", {"application": ["like", "GEN-%"]}),
        ("Consular Fee Waiver", {"application": ["like", "GEN-%"]}),
        ("Consular Fee Rule", {"service": ["in", SAMPLE_SERVICE_CODES]}),
        ("Consular Service Document Requirement", {"parent": ["in", SAMPLE_SERVICE_CODES]}),
    ):
        if frappe.db.exists("DocType", doctype):
            frappe.db.delete(doctype, filters)

    for doctype in (
        "Visa Application Details",
        "Passport Service Details",
        "Consular Card Details",
        "Attestation Legalisation Details",
        "Emergency Travel Document Details",
        "Civil Registry Details",
    ):
        if frappe.db.exists("DocType", doctype):
            frappe.db.delete(doctype, {"consular_application": ["like", "GEN-%"]})

    if frappe.db.exists("DocType", "Consular Application"):
        frappe.db.delete("Consular Application", {"name": ["like", "GEN-%"]})

    if frappe.db.exists("DocType", "Consular Service"):
        for code in SAMPLE_SERVICE_CODES:
            if frappe.db.exists("Consular Service", code):
                frappe.delete_doc("Consular Service", code, force=True, ignore_permissions=True)

    if frappe.db.exists("DocType", "Appointment Location") and frappe.db.exists("Appointment Location", SAMPLE_LOCATION):
        frappe.delete_doc("Appointment Location", SAMPLE_LOCATION, force=True, ignore_permissions=True)

    frappe.db.commit()
    return "EMSDEMO sample data cleared."
