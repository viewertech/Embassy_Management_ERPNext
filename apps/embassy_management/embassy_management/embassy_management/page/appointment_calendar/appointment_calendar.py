import frappe

from embassy_management.embassy_management.display_titles import link_title


@frappe.whitelist()
def upcoming(limit=100):
    rows = frappe.get_all(
        "Embassy Appointment",
        fields=["name", "booking_code", "service", "appointment_date", "start_time", "status", "location", "officer"],
        order_by="appointment_date asc, start_time asc",
        limit_page_length=int(limit),
    )
    for row in rows:
        row.service_label = link_title("Consular Service", row.service, "service_name")
        row.location_label = link_title("Appointment Location", row.location, "location_name")
        row.officer_label = link_title("User", row.officer)
    return rows
