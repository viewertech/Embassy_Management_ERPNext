from frappe.model.document import Document


class ConsularService(Document):
    def validate(self):
        if self.service_code:
            self.service_code = self.service_code.strip().upper().replace(" ", "-")
