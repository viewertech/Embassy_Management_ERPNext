from __future__ import annotations

import frappe


ADMIN_ROLES = {"System Manager", "Embassy Administrator"}
SUPERVISOR_ROLES = {"Consular Supervisor", "Head of Consular Section", "Head of Mission"}
OFFICER_ROLES = {
    "Consular Officer",
    "Visa Officer",
    "Passport Officer",
    "Appointment Officer",
    "Cashier / Finance Officer",
}


def _roles(user):
    return set(frappe.get_roles(user))


def _applicant_profile(user):
    return frappe.db.get_value("Embassy Applicant Profile", {"user": user}, "name")


def _is_admin_or_supervisor(user):
    roles = _roles(user)
    return bool(roles & (ADMIN_ROLES | SUPERVISOR_ROLES))


def get_consular_application_permission_query_conditions(user=None):
    user = user or frappe.session.user
    if user == "Administrator" or _is_admin_or_supervisor(user):
        return ""
    roles = _roles(user)
    if "Applicant" in roles:
        profile = _applicant_profile(user)
        if not profile:
            return "1=0"
        return f"`tabConsular Application`.`applicant` = {frappe.db.escape(profile)}"
    if roles & OFFICER_ROLES:
        escaped = frappe.db.escape(user)
        queue_statuses = "', '".join([
            "Submitted", "Payment Confirmed", "Appointment Booked",
            "Under Initial Review", "Awaiting Additional Documents",
            "Awaiting Interview", "Under Officer Review",
        ])
        return f"(`tabConsular Application`.`assigned_officer` = {escaped} OR `tabConsular Application`.`application_status` IN ('{queue_statuses}'))"
    return "1=0"


def has_consular_application_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user
    if user == "Administrator" or _is_admin_or_supervisor(user):
        return True
    roles = _roles(user)
    if "Applicant" in roles:
        return doc.applicant and doc.applicant == _applicant_profile(user)
    if roles & OFFICER_ROLES:
        return True
    return False


def get_uploaded_document_permission_query_conditions(user=None):
    user = user or frappe.session.user
    if user == "Administrator" or _is_admin_or_supervisor(user) or (_roles(user) & OFFICER_ROLES):
        return ""
    profile = _applicant_profile(user)
    if not profile:
        return "1=0"
    apps = frappe.get_all("Consular Application", filters={"applicant": profile}, pluck="name")
    if not apps:
        return "1=0"
    escaped = ", ".join(frappe.db.escape(app) for app in apps)
    return f"`tabApplication Uploaded Document`.`application` IN ({escaped})"


def has_uploaded_document_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user
    if user == "Administrator" or _is_admin_or_supervisor(user) or (_roles(user) & OFFICER_ROLES):
        return True
    app = frappe.get_doc("Consular Application", doc.application)
    return has_consular_application_permission(app, user, permission_type)


def get_appointment_permission_query_conditions(user=None):
    user = user or frappe.session.user
    if user == "Administrator" or _is_admin_or_supervisor(user) or (_roles(user) & OFFICER_ROLES):
        return ""
    profile = _applicant_profile(user)
    if not profile:
        return "1=0"
    return f"`tabEmbassy Appointment`.`applicant` = {frappe.db.escape(profile)}"


def has_appointment_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user
    if user == "Administrator" or _is_admin_or_supervisor(user) or (_roles(user) & OFFICER_ROLES):
        return True
    return doc.applicant and doc.applicant == _applicant_profile(user)
