import frappe


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
