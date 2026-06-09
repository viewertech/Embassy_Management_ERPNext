import frappe
from frappe.model.document import Document

from embassy_management.embassy_management.display_titles import build_payment_review_title


class ConsularPaymentReview(Document):
    def validate(self):
        self.review_title = build_payment_review_title(self)
