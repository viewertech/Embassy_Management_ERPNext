from __future__ import annotations

import csv
from pathlib import Path

import frappe


ROLES = [
    "Applicant", "Consular Officer", "Visa Officer", "Passport Officer", "Appointment Officer",
    "Cashier / Finance Officer", "Consular Supervisor", "Head of Consular Section",
    "Head of Mission", "Embassy Administrator",
]

APP_NAME = "embassy_management"
APP_TITLE = "Embassy Management"
APP_ROUTE = "/desk/embassy-management"
APP_ICON = "/assets/embassy_management/img/app_icon.png"


def create_admin_user(email, first_name="Embassy", last_name="Administrator", password=None):
    if frappe.db.exists("User", email):
        user = frappe.get_doc("User", email)
    else:
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "send_welcome_email": 0,
            "enabled": 1,
        }).insert(ignore_permissions=True)
    for role in ["Embassy Administrator", "System Manager"]:
        user.add_roles(role)
    if password:
        user.new_password = password
        user.save(ignore_permissions=True)
    frappe.db.commit()
    return user.name


def ensure_roles():
    for role_name in ROLES:
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({"doctype": "Role", "role_name": role_name, "desk_access": 1}).insert(ignore_permissions=True)


def sync_desktop_integration():
    if not frappe.db.table_exists("Desktop Icon"):
        return

    icon_name = (
        frappe.db.exists("Desktop Icon", {"icon_type": "App", "app": APP_NAME})
        or frappe.db.exists("Desktop Icon", {"label": APP_TITLE, "icon_type": "App"})
        or frappe.db.exists("Desktop Icon", {"label": APP_TITLE})
    )

    values = {
        "label": APP_TITLE,
        "icon_type": "App",
        "link_type": "External",
        "app": APP_NAME,
        "link": APP_ROUTE,
        "logo_url": APP_ICON,
        "icon_image": APP_ICON,
        "standard": 1,
        "hidden": 0,
        "bg_color": "blue",
    }

    if icon_name:
        icon = frappe.get_doc("Desktop Icon", icon_name)
        dirty = False
        for field, value in values.items():
            if icon.get(field) != value:
                icon.set(field, value)
                dirty = True
        if dirty:
            icon.save(ignore_permissions=True)
    else:
        icon = frappe.get_doc({"doctype": "Desktop Icon", "name": APP_TITLE, **values})
        icon.insert(ignore_permissions=True, ignore_if_duplicate=True)

    frappe.clear_cache()


def import_sample_data():
    ensure_roles()
    if not frappe.db.exists("Appointment Location", "Generic Consular Counter"):
        location = frappe.new_doc("Appointment Location")
        location.location_name = "Generic Consular Counter"
        location.active = 1
        location.insert(ignore_permissions=True)

    app_path = Path(frappe.get_app_path("embassy_management")).resolve()
    candidates = [
        app_path / "sample_data",
        app_path.parent / "sample_data",
        app_path.parent.parent / "sample_data",
        Path("/home/frappe/frappe-bench/sample_data"),
    ]
    base = next((path for path in candidates if path.exists()), None)
    if not base:
        frappe.logger("embassy_management").warning("Sample data folder not found in candidates: %s", candidates)
        return
    for csv_name, doctype in [
        ("consular_services.csv", "Consular Service"),
        ("fee_rules.csv", "Consular Fee Rule"),
        ("document_requirements.csv", "Consular Service Document Requirement"),
        ("appointment_slots.csv", "Appointment Slot"),
    ]:
        path = base / csv_name
        if not path.exists():
            continue
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if not row:
                    continue
                name = row.get("name")
                if name and frappe.db.exists(doctype, name):
                    continue
                if _sample_row_exists(doctype, row):
                    continue
                doc = frappe.new_doc(doctype)
                for key, value in row.items():
                    if key and value != "":
                        doc.set(key, value)
                doc.insert(ignore_permissions=True)
    frappe.db.commit()


def _sample_row_exists(doctype, row):
    if doctype == "Consular Fee Rule":
        return bool(
            frappe.db.exists(
                doctype,
                {
                    "service": row.get("service"),
                    "visa_type": row.get("visa_type") or "",
                    "processing_type": row.get("processing_type") or "Normal",
                    "entry_type": row.get("entry_type") or "",
                    "amount": row.get("amount"),
                    "currency": row.get("currency"),
                },
            )
        )
    if doctype == "Consular Service Document Requirement":
        return bool(
            frappe.db.exists(
                doctype,
                {
                    "parent": row.get("parent"),
                    "parenttype": row.get("parenttype"),
                    "requirement_label": row.get("requirement_label"),
                },
            )
        )
    if doctype == "Appointment Slot":
        return bool(
            frappe.db.exists(
                doctype,
                {
                    "service": row.get("service"),
                    "location": row.get("location"),
                    "slot_date": row.get("slot_date"),
                    "from_time": row.get("from_time"),
                },
            )
        )
    return False
