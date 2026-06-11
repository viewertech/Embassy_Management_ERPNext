import frappe

from embassy_management.embassy_management.display_titles import (
    build_fee_rule_title,
    build_fee_waiver_title,
    build_payment_review_title,
    build_service_details_title,
    link_title,
    truncate_title,
)


DETAIL_TITLE_CONFIG = {
    "Visa Application Details": ("Visa Details", ["visa_type", "entry_type"]),
    "Passport Service Details": (
        "Passport Details",
        ["service_request_type", "passport_type", "passport_number"],
    ),
    "Consular Card Details": (
        "Consular Card Details",
        ["current_nationality", "diaspora_registration_number"],
    ),
    "Attestation Legalisation Details": (
        "Attestation Details",
        ["document_type", "document_owner", "legalisation_type"],
    ),
    "Emergency Travel Document Details": (
        "Emergency Travel Document Details",
        ["reason", "destination_country", "travel_date"],
    ),
    "Civil Registry Details": (
        "Civil Registry Details",
        ["registry_service_type", "related_person", "event_date"],
    ),
}


def execute():
    doctypes = [
        "consular_fee_rule",
        "consular_fee_waiver",
        "consular_payment_review",
        "visa_application_details",
        "passport_service_details",
        "consular_card_details",
        "attestation_legalisation_details",
        "emergency_travel_document_details",
        "civil_registry_details",
        "application_form_template",
        "application_form_section",
        "application_form_field",
        "application_form_rule",
        "appointment_officer",
        "appointment_location",
        "appointment_service_type",
    ]
    for doctype in doctypes:
        frappe.reload_doc("embassy_management", "doctype", doctype)

    _backfill(
        "Consular Fee Rule",
        "fee_rule_title",
        build_fee_rule_title,
        [
            "service",
            "visa_type",
            "nationality",
            "residence_country",
            "processing_type",
            "entry_type",
            "amount",
            "currency",
        ],
    )
    _backfill(
        "Consular Fee Waiver",
        "waiver_title",
        build_fee_waiver_title,
        ["application", "waiver_type", "amount", "currency"],
    )
    _backfill(
        "Consular Payment Review",
        "review_title",
        build_payment_review_title,
        ["application", "review_status", "amount", "currency"],
    )

    for doctype, (label, detail_fields) in DETAIL_TITLE_CONFIG.items():
        _backfill(
            doctype,
            "details_title",
            lambda row, label=label, detail_fields=detail_fields: build_service_details_title(
                row,
                label,
                detail_fields,
            ),
            ["consular_application", *detail_fields],
        )

    for row in frappe.get_all("Appointment Officer", fields=["name", "user", "display_name"]):
        if row.user and not row.display_name:
            frappe.db.set_value(
                "Appointment Officer",
                row.name,
                "display_name",
                link_title("User", row.user),
                update_modified=False,
            )


def _backfill(doctype, title_field, builder, fields):
    for row in frappe.get_all(doctype, fields=["name", *fields]):
        title = builder(row)
        if title:
            frappe.db.set_value(doctype, row.name, title_field, truncate_title(title), update_modified=False)
