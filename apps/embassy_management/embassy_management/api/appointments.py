from __future__ import annotations

import frappe
from frappe import _

from embassy_management.utils import get_or_create_applicant_profile


@frappe.whitelist(allow_guest=True)
def available_slots(service=None, location=None, from_date=None, to_date=None):
    filters = {"active": 1}
    if service:
        filters["service"] = service
    if location:
        filters["location"] = location
    if from_date and to_date:
        filters["slot_date"] = ["between", [from_date, to_date]]
    elif from_date:
        filters["slot_date"] = [">=", from_date]
    return frappe.get_all(
        "Appointment Slot",
        filters=filters,
        fields=["name", "service", "location", "officer", "slot_date", "from_time", "to_time", "capacity", "booked_count"],
        order_by="slot_date asc, from_time asc",
    )


@frappe.whitelist()
def book_slot(application, slot):
    profile = get_or_create_applicant_profile()
    app = frappe.get_doc("Consular Application", application)
    app.check_permission("write")
    slot_doc = frappe.get_doc("Appointment Slot", slot)
    if slot_doc.booked_count >= slot_doc.capacity:
        frappe.throw(_("This appointment slot is full."))
    appointment = frappe.new_doc("Embassy Appointment")
    appointment.application = app.name
    appointment.applicant = profile.name
    appointment.service = app.service
    appointment.slot = slot_doc.name
    appointment.location = slot_doc.location
    appointment.officer = slot_doc.officer
    appointment.appointment_date = slot_doc.slot_date
    appointment.start_time = slot_doc.from_time
    appointment.end_time = slot_doc.to_time
    appointment.status = "Booked"
    appointment.insert()
    slot_doc.booked_count = (slot_doc.booked_count or 0) + 1
    slot_doc.save(ignore_permissions=True)
    app.appointment = appointment.name
    app.booking_code = appointment.booking_code
    app.application_status = "Appointment Booked"
    app.save()
    return appointment.as_dict()
