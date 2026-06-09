import frappe

from embassy_management.embassy_management.display_titles import application_label


@frappe.whitelist()
def summary():
    pending = frappe.db.count("Consular Application", {"payment_status": ["in", ["Payment Pending", "Payment Under Review"]]})
    confirmed = frappe.db.count("Consular Application", {"payment_status": "Payment Confirmed"})
    reviews = frappe.get_all(
        "Consular Payment Review",
        fields=["name", "review_title", "application", "amount", "currency", "review_status", "modified"],
        order_by="modified desc",
        limit_page_length=25,
    )
    for review in reviews:
        review.application_label = application_label(review.application)
    return {"pending": pending, "confirmed": confirmed, "reviews": reviews}
