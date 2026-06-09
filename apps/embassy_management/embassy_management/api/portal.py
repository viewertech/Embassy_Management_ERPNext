from __future__ import annotations

import frappe
from frappe import _

from embassy_management.embassy_management.display_titles import link_title
from embassy_management.api.requirements import evaluate_requirements
from embassy_management.utils import get_or_create_applicant_profile


@frappe.whitelist(allow_guest=True)
def get_public_services():
    return frappe.get_all(
        "Consular Service",
        filters={"enabled_on_public_portal": 1},
        fields=[
            "name", "service_name", "service_code", "service_category", "description",
            "requires_appointment", "requires_online_application", "requires_document_upload",
            "requires_payment", "default_processing_time", "default_fee", "currency",
        ],
        order_by="service_category asc, service_name asc",
    )


@frappe.whitelist()
def create_application(service, submission_channel="Online"):
    profile = get_or_create_applicant_profile()
    service_doc = frappe.get_doc("Consular Service", service)
    application = frappe.new_doc("Consular Application")
    application.applicant = profile.name
    application.customer = profile.customer
    application.contact = profile.contact
    application.service = service_doc.name
    application.application_status = "Draft"
    application.submission_channel = submission_channel
    application.priority = "Normal"
    application.currency = service_doc.currency
    requirement_data = evaluate_requirements(service)
    application.total_fee = requirement_data.get("fee") or service_doc.default_fee or 0
    application.insert()
    _create_application_requirements(application.name, service)
    return application.as_dict()


@frappe.whitelist()
def save_application(application, data=None, progress_percent=None):
    doc = frappe.get_doc("Consular Application", application)
    doc.check_permission("write")
    if doc.locked_after_submission:
        frappe.throw(_("Submitted applications cannot be edited from the portal."))
    if data:
        doc.applicant_notes = data
    if progress_percent is not None:
        doc.progress_percent = progress_percent
    doc.save()
    return doc.as_dict()


@frappe.whitelist()
def submit_application(application, declaration_accepted=False, privacy_consent=False, terms_accepted=False):
    doc = frappe.get_doc("Consular Application", application)
    doc.check_permission("write")
    if not (frappe.parse_json(declaration_accepted) and frappe.parse_json(privacy_consent) and frappe.parse_json(terms_accepted)):
        frappe.throw(_("Please accept the declaration, privacy notice, and terms before submitting."))
    missing = frappe.get_all(
        "Application Document Requirement",
        filters={"application": doc.name, "mandatory": 1},
        pluck="name",
    )
    uploaded = set(frappe.get_all("Application Uploaded Document", filters={"application": doc.name}, pluck="requirement"))
    missing = [name for name in missing if name not in uploaded]
    if missing:
        frappe.throw(_("Please upload all mandatory documents before submitting."))
    doc.declaration_accepted = 1
    doc.privacy_consent = 1
    doc.terms_accepted = 1
    doc.application_status = "Submitted"
    doc.locked_after_submission = 1
    doc.submitted_on = frappe.utils.now()
    doc.save()
    return doc.as_dict()


@frappe.whitelist()
def applicant_dashboard():
    profile = get_or_create_applicant_profile()
    applications = frappe.get_all(
        "Consular Application",
        filters={"applicant": profile.name},
        fields=["name", "application_number", "service", "application_status", "payment_status", "modified", "total_fee", "currency"],
        order_by="modified desc",
    )
    appointments = frappe.get_all(
        "Embassy Appointment",
        filters={"applicant": profile.name},
        fields=["name", "booking_code", "service", "appointment_date", "start_time", "status"],
        order_by="appointment_date desc",
    )
    for application in applications:
        application.service_label = link_title("Consular Service", application.service, "service_name")
    for appointment in appointments:
        appointment.service_label = link_title("Consular Service", appointment.service, "service_name")
    return {"profile": profile.as_dict(), "applications": applications, "appointments": appointments}


def _create_application_requirements(application, service):
    existing = frappe.get_all("Application Document Requirement", filters={"application": application}, pluck="name")
    if existing:
        return
    rows = frappe.get_all(
        "Consular Service Document Requirement",
        filters={"parent": service, "parenttype": "Consular Service"},
        fields=["document_category", "requirement_label", "mandatory", "allowed_file_types", "max_file_size_mb", "instructions"],
        order_by="idx asc",
    )
    for row in rows:
        req = frappe.new_doc("Application Document Requirement")
        req.application = application
        req.service = service
        req.document_category = row.document_category
        req.requirement_label = row.requirement_label
        req.mandatory = row.mandatory
        req.allowed_file_types = row.allowed_file_types
        req.max_file_size_mb = row.max_file_size_mb
        req.instructions = row.instructions
        req.insert(ignore_permissions=True)
