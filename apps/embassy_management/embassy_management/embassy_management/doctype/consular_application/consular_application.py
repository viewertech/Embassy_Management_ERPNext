import frappe
from frappe.model.document import Document


class ConsularApplication(Document):
    def before_insert(self):
        settings = frappe.get_single("Embassy Settings") if frappe.db.exists("DocType", "Embassy Settings") else None
        if settings:
            self.embassy_mission = settings.embassy_mission_name
            self.currency = self.currency or settings.default_currency
        self.last_updated_on = frappe.utils.now()

    def after_insert(self):
        if not self.application_number:
            self.db_set("application_number", self.name, update_modified=False)

    def validate(self):
        self.last_updated_on = frappe.utils.now()
        if self.application_status != "Draft" and not self.submitted_on:
            self.submitted_on = frappe.utils.now()
        if self.decision and not self.decision_date:
            self.decision_date = frappe.utils.today()
