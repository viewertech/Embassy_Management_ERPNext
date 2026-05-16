import frappe
from frappe.model.document import Document


class ApplicationUploadedDocument(Document):
    def before_insert(self):
        self.uploaded_by = self.uploaded_by or frappe.session.user

    def validate(self):
        if self.status in {"Accepted", "Rejected", "Unclear", "Expired", "Missing", "Re-upload Requested"}:
            self.reviewed_by = self.reviewed_by or frappe.session.user
            self.reviewed_on = self.reviewed_on or frappe.utils.now()
