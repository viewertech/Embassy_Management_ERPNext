import frappe
from frappe.model.document import Document

from embassy_management.embassy_management.display_titles import link_title


class AppointmentOfficer(Document):
    def validate(self):
        if self.user and not self.display_name:
            self.display_name = link_title("User", self.user)
