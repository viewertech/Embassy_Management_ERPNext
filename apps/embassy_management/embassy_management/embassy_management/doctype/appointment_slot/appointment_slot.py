import frappe
from frappe.model.document import Document


def _field(doc, fieldname):
    if isinstance(doc, dict):
        return doc.get(fieldname)
    return getattr(doc, fieldname, None)


def _link_title(doctype, name, title_field):
    if not name:
        return None
    return frappe.db.get_value(doctype, name, title_field) or name


def _format_time(value):
    if not value:
        return None
    text = str(value)
    if "." in text:
        text = text.split(".", 1)[0]
    return text[:5] if len(text) >= 5 else text


def build_slot_label(doc):
    service = _link_title("Consular Service", _field(doc, "service"), "service_name")
    appointment_type = _link_title(
        "Appointment Service Type",
        _field(doc, "appointment_service_type"),
        "service_type_name",
    )
    location = _link_title("Appointment Location", _field(doc, "location"), "location_name")
    date = _field(doc, "slot_date")
    time_range = " - ".join(
        part
        for part in (
            _format_time(_field(doc, "from_time")),
            _format_time(_field(doc, "to_time")),
        )
        if part
    )
    parts = [service or appointment_type or "Appointment Slot", location, str(date) if date else None, time_range]
    return " | ".join(part for part in parts if part)


class AppointmentSlot(Document):
    def validate(self):
        self.slot_label = build_slot_label(self)
