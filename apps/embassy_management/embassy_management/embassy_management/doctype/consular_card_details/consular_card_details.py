import frappe
from frappe.model.document import Document

from embassy_management.embassy_management.display_titles import build_service_details_title


class ConsularCardDetails(Document):
    def validate(self):
        self.details_title = build_service_details_title(
            self,
            "Consular Card Details",
            ["current_nationality", "diaspora_registration_number"],
        )
