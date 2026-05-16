import frappe


def send_appointment_reminders():
    # Notification documents should own message content; this task only marks the daily hook.
    frappe.logger("embassy_management").info("Appointment reminder scheduler executed.")


def mark_overdue_applications():
    statuses = ["Submitted", "Under Initial Review", "Awaiting Interview", "Under Officer Review"]
    for row in frappe.get_all("Consular Application", filters={"application_status": ["in", statuses]}, fields=["name"]):
        frappe.db.set_value("Consular Application", row.name, "last_updated_on", frappe.utils.now(), update_modified=False)
