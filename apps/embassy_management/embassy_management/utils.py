from __future__ import annotations

import json
from typing import Any

import frappe
from frappe import _


OFFICER_ROLES = {
    "Consular Officer",
    "Visa Officer",
    "Passport Officer",
    "Appointment Officer",
    "Cashier / Finance Officer",
    "Consular Supervisor",
    "Head of Consular Section",
    "Head of Mission",
    "Embassy Administrator",
    "System Manager",
}


def get_embassy_settings() -> dict[str, Any]:
    if not frappe.db.exists("DocType", "Embassy Settings"):
        return {}
    return frappe.get_single("Embassy Settings").as_dict()


def parse_json(value: str | dict | list | None, fallback=None):
    if value in (None, ""):
        return fallback if fallback is not None else {}
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return fallback if fallback is not None else {}


def user_has_officer_role(user: str | None = None) -> bool:
    user = user or frappe.session.user
    return bool(set(frappe.get_roles(user)) & OFFICER_ROLES)


def get_or_create_applicant_profile(user: str | None = None):
    user = user or frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please sign in to continue."))
    existing = frappe.db.get_value("Embassy Applicant Profile", {"user": user}, "name")
    if existing:
        return frappe.get_doc("Embassy Applicant Profile", existing)
    user_doc = frappe.get_doc("User", user)
    profile = frappe.new_doc("Embassy Applicant Profile")
    profile.user = user
    profile.full_name = user_doc.full_name or user_doc.email
    profile.email = user_doc.email
    profile.preferred_language = frappe.local.lang or "en"
    profile.insert(ignore_permissions=True)
    return profile


def apply_brand_context(context):
    settings = get_embassy_settings()
    context.brand = {
        "mission_name": settings.get("embassy_mission_name") or "Embassy Management",
        "primary_colour": settings.get("primary_brand_colour") or "#144870",
        "secondary_colour": settings.get("secondary_brand_colour") or "#e6b654",
        "logo": settings.get("mission_logo"),
        "footer": settings.get("email_footer") or "Powered by Viewertech",
        "viewertech_url": "https://viewertech.net",
    }
    return context
