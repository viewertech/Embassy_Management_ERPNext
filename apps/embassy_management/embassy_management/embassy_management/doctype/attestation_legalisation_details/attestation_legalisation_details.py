import frappe
from frappe.model.document import Document

from embassy_management.embassy_management.display_titles import build_service_details_title


class AttestationLegalisationDetails(Document):
    def validate(self):
        self.details_title = build_service_details_title(
            self,
            "Attestation Details",
            ["document_type", "document_owner", "legalisation_type"],
        )
