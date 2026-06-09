import frappe
from frappe.model.document import Document

from embassy_management.embassy_management.display_titles import build_service_details_title


class CivilRegistryDetails(Document):
    def validate(self):
        self.details_title = build_service_details_title(
            self,
            "Civil Registry Details",
            ["registry_service_type", "related_person", "event_date"],
        )
