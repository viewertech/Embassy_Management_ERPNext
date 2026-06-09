import frappe
from frappe.model.document import Document

from embassy_management.embassy_management.display_titles import build_fee_waiver_title


class ConsularFeeWaiver(Document):
    def validate(self):
        self.waiver_title = build_fee_waiver_title(self)
