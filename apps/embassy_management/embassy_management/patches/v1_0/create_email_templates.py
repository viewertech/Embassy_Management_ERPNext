import frappe


TEMPLATES = {
    "EMS - Application Submitted": ("Application submitted", "Your application {{ doc.application_number }} has been submitted."),
    "EMS - Payment Pending": ("Payment pending", "Payment is pending for application {{ doc.application_number }}."),
    "EMS - Appointment Booked": ("Appointment booked", "Your appointment has been booked. Booking code: {{ doc.booking_code }}."),
    "EMS - Additional Documents Requested": ("Additional documents requested", "Additional documents are required for {{ doc.application_number }}."),
    "EMS - Application Approved": ("Application approved", "Your application {{ doc.application_number }} has been approved."),
    "EMS - Application Rejected": ("Application rejected", "Your application {{ doc.application_number }} has been rejected. Please review the reason in your portal."),
}


def execute():
    for name, (subject, response) in TEMPLATES.items():
        if frappe.db.exists("Email Template", name):
            continue
        frappe.get_doc({
            "doctype": "Email Template",
            "name": name,
            "subject": subject,
            "response": response + "<br><br>Powered by Viewertech",
            "use_html": 1,
        }).insert(ignore_permissions=True)
