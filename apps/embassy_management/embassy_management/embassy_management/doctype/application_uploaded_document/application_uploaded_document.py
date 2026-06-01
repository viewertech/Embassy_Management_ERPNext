import frappe
from frappe.model.document import Document


def _field(doc, fieldname):
    if isinstance(doc, dict):
        return doc.get(fieldname)
    return getattr(doc, fieldname, None)


def build_document_title(doc):
    application = _field(doc, "application")
    requirement = _field(doc, "requirement")
    category = _field(doc, "document_category")
    status = _field(doc, "status")

    application_label = application
    applicant_name = None
    if application:
        application_doc = frappe.db.get_value(
            "Consular Application",
            application,
            ["application_number", "applicant"],
            as_dict=True,
        )
        if application_doc:
            application_label = application_doc.application_number or application
            if application_doc.applicant:
                applicant_name = frappe.db.get_value(
                    "Embassy Applicant Profile",
                    application_doc.applicant,
                    "full_name",
                )

    requirement_label = None
    if requirement:
        requirement_label = frappe.db.get_value(
            "Application Document Requirement",
            requirement,
            "requirement_label",
        )

    label = requirement_label or category or "Uploaded Document"
    return " | ".join(part for part in [label, application_label, applicant_name, status] if part)


class ApplicationUploadedDocument(Document):
    def before_insert(self):
        self.uploaded_by = self.uploaded_by or frappe.session.user

    def validate(self):
        self.document_title = build_document_title(self)
        if self.status in {"Accepted", "Rejected", "Unclear", "Expired", "Missing", "Re-upload Requested"}:
            self.reviewed_by = self.reviewed_by or frappe.session.user
            self.reviewed_on = self.reviewed_on or frappe.utils.now()
