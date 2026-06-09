import frappe
from frappe.model.document import Document

from embassy_management.embassy_management.display_titles import build_service_details_title


class PassportServiceDetails(Document):
    def validate(self):
        self.details_title = build_service_details_title(
            self,
            "Passport Details",
            ["service_request_type", "passport_type", "passport_number"],
        )
