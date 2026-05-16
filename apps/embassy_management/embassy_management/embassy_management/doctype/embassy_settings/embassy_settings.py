import frappe
from frappe.model.document import Document


class EmbassySettings(Document):
    def validate(self):
        if self.website and not self.website.startswith(("http://", "https://")):
            self.website = "https://" + self.website
