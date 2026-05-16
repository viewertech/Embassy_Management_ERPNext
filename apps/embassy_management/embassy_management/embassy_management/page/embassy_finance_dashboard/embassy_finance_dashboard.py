import frappe


@frappe.whitelist()
def summary():
    pending = frappe.db.count("Consular Application", {"payment_status": ["in", ["Payment Pending", "Payment Under Review"]]})
    confirmed = frappe.db.count("Consular Application", {"payment_status": "Payment Confirmed"})
    reviews = frappe.get_all(
        "Consular Payment Review",
        fields=["name", "application", "amount", "currency", "review_status", "modified"],
        order_by="modified desc",
        limit_page_length=25,
    )
    return {"pending": pending, "confirmed": confirmed, "reviews": reviews}
