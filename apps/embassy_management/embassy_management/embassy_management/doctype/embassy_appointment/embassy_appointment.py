import frappe
from frappe.model.document import Document


class EmbassyAppointment(Document):
    def after_insert(self):
        if not self.booking_code:
            self.db_set("booking_code", self.name, update_modified=False)
