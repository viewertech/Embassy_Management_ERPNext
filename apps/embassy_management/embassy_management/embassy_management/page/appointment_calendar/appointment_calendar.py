import frappe


@frappe.whitelist()
def upcoming(limit=100):
    return frappe.get_all(
        "Embassy Appointment",
        fields=["name", "booking_code", "service", "appointment_date", "start_time", "status", "location", "officer"],
        order_by="appointment_date asc, start_time asc",
        limit_page_length=int(limit),
    )
