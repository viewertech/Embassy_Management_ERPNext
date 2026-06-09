import frappe

from embassy_management.embassy_management.display_titles import link_title


@frappe.whitelist()
def get_context():
    return {
        "pending_statuses": [
            "Submitted",
            "Payment Confirmed",
            "Appointment Booked",
            "Under Initial Review",
            "Awaiting Additional Documents",
            "Awaiting Interview",
            "Under Officer Review",
        ]
    }


@frappe.whitelist()
def case_queue(filters=None, limit=50):
    filters = frappe.parse_json(filters) if isinstance(filters, str) else filters
    filters = filters or {}
    rows = frappe.get_all(
        "Consular Application",
        fields=[
            "name",
            "application_number",
            "service",
            "application_status",
            "priority",
            "assigned_officer",
            "modified",
        ],
        filters=filters,
        limit_page_length=int(limit),
        order_by="modified asc",
    )
    for row in rows:
        row.service_label = link_title("Consular Service", row.service, "service_name")
        row.assigned_officer_label = link_title("User", row.assigned_officer)
    return rows
