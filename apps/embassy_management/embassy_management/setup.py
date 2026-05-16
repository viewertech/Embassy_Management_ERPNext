from __future__ import annotations

import csv
from pathlib import Path

import frappe


ROLES = [
    "Applicant", "Consular Officer", "Visa Officer", "Passport Officer", "Appointment Officer",
    "Cashier / Finance Officer", "Consular Supervisor", "Head of Consular Section",
    "Head of Mission", "Embassy Administrator",
]


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


def import_sample_data():
    ensure_roles()
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
                doc = frappe.new_doc(doctype)
                for key, value in row.items():
                    if key and value != "":
                        doc.set(key, value)
                doc.insert(ignore_permissions=True)
    frappe.db.commit()
