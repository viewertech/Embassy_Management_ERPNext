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
def case_queue(filters=None, service_query=None, officer_query=None, limit=50):
    filters = frappe.parse_json(filters) if isinstance(filters, str) else filters
    filters = filters or {}
    filters = _normalize_case_filters(filters, service_query, officer_query)
    if filters is None:
        return []
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


def _normalize_case_filters(filters, service_query=None, officer_query=None):
    filters = dict(filters)
    service_query = service_query or filters.pop("service_query", None)
    officer_query = officer_query or filters.pop("officer_query", None)

    if service_query:
        services = _find_services(service_query)
        if not services:
            return None
        filters["service"] = ["in", services]

    if officer_query:
        officers = _find_users(officer_query)
        if not officers:
            return None
        filters["assigned_officer"] = ["in", officers]

    return filters


def _find_services(text):
    text = f"%{text}%"
    return frappe.get_all(
        "Consular Service",
        or_filters=[
            ["Consular Service", "service_name", "like", text],
            ["Consular Service", "name", "like", text],
            ["Consular Service", "service_code", "like", text],
        ],
        pluck="name",
        limit_page_length=20,
    )


def _find_users(text):
    text = f"%{text}%"
    return frappe.get_all(
        "User",
        filters=[["User", "enabled", "=", 1]],
        or_filters=[
            ["User", "name", "like", text],
            ["User", "full_name", "like", text],
            ["User", "email", "like", text],
        ],
        pluck="name",
        limit_page_length=20,
    )
