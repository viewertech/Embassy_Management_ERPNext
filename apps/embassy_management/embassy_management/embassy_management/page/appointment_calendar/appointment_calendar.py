import frappe

from embassy_management.embassy_management.display_titles import link_title


@frappe.whitelist()
def upcoming(limit=100, status=None, service_query=None, location_query=None, from_date=None, to_date=None):
    filters = {}
    if status:
        filters["status"] = status
    if from_date and to_date:
        filters["appointment_date"] = ["between", [from_date, to_date]]
    elif from_date:
        filters["appointment_date"] = [">=", from_date]
    elif to_date:
        filters["appointment_date"] = ["<=", to_date]

    services = _find_services(service_query)
    if service_query and not services:
        return []
    if services:
        filters["service"] = ["in", services]

    locations = _find_locations(location_query)
    if location_query and not locations:
        return []
    if locations:
        filters["location"] = ["in", locations]

    rows = frappe.get_all(
        "Embassy Appointment",
        filters=filters,
        fields=["name", "booking_code", "service", "appointment_date", "start_time", "status", "location", "officer"],
        order_by="appointment_date asc, start_time asc",
        limit_page_length=int(limit),
    )
    for row in rows:
        row.service_label = link_title("Consular Service", row.service, "service_name")
        row.location_label = link_title("Appointment Location", row.location, "location_name")
        row.officer_label = link_title("User", row.officer)
    return rows


def _find_services(text):
    if not text:
        return []
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


def _find_locations(text):
    if not text:
        return []
    text = f"%{text}%"
    return frappe.get_all(
        "Appointment Location",
        or_filters=[
            ["Appointment Location", "location_name", "like", text],
            ["Appointment Location", "name", "like", text],
        ],
        pluck="name",
        limit_page_length=20,
    )
