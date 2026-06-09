import frappe
from frappe.model.document import Document

from embassy_management.embassy_management.display_titles import build_fee_rule_title


class ConsularFeeRule(Document):
    def validate(self):
        self.fee_rule_title = build_fee_rule_title(self)
