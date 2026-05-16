from __future__ import annotations

import frappe

from embassy_management.utils import parse_json


OPERATORS = {
    "Equals": lambda actual, expected: str(actual or "") == str(expected or ""),
    "Not Equals": lambda actual, expected: str(actual or "") != str(expected or ""),
    "In": lambda actual, expected: str(actual or "") in [x.strip() for x in str(expected or "").split(",")],
    "Not In": lambda actual, expected: str(actual or "") not in [x.strip() for x in str(expected or "").split(",")],
    "Is Set": lambda actual, expected: bool(actual),
    "Is Not Set": lambda actual, expected: not bool(actual),
}


def _rule_matches(rule, context):
    actual = context.get(rule.trigger_field)
    operator = rule.operator or "Equals"
    return OPERATORS.get(operator, OPERATORS["Equals"])(actual, rule.value)


@frappe.whitelist(allow_guest=True)
def evaluate_requirements(service, nationality=None, residence_country=None, visa_type=None, entry_type=None, processing_type=None):
    context = {
        "service": service,
        "nationality": nationality,
        "residence_country": residence_country,
        "visa_type": visa_type,
        "entry_type": entry_type,
        "processing_type": processing_type or "Normal",
    }
    service_doc = frappe.get_doc("Consular Service", service)
    requirements = frappe.get_all(
        "Consular Service Document Requirement",
        filters={"parent": service, "parenttype": "Consular Service"},
        fields=["document_category", "requirement_label", "mandatory", "allowed_file_types", "max_file_size_mb", "instructions"],
        order_by="idx asc",
    )
    notices = []
    eligibility = "Eligible"
    appointment_required = bool(service_doc.requires_appointment)
    fee = service_doc.default_fee or 0
    currency = service_doc.currency

    rules = frappe.get_all(
        "Application Form Rule",
        filters={"enabled": 1, "service": service},
        fields=["name", "rule_type", "trigger_field", "operator", "value", "action_target", "action_payload", "notice_title", "notice_message"],
        order_by="priority asc, modified asc",
    )
    for rule_name in [r.name for r in rules]:
        rule = frappe.get_doc("Application Form Rule", rule_name)
        if not _rule_matches(rule, context):
            continue
        payload = parse_json(rule.action_payload, {})
        if rule.rule_type == "Trigger Notice":
            notices.append({"title": rule.notice_title, "message": rule.notice_message})
        elif rule.rule_type == "Require Appointment":
            appointment_required = True
        elif rule.rule_type == "Restrict Eligibility":
            eligibility = payload.get("message") or rule.notice_message or "Not eligible"
        elif rule.rule_type == "Require Document":
            requirements.append({
                "document_category": payload.get("document_category") or "Other Documents",
                "requirement_label": payload.get("requirement_label") or rule.action_target,
                "mandatory": 1,
                "allowed_file_types": payload.get("allowed_file_types") or "pdf,jpg,jpeg,png",
                "max_file_size_mb": payload.get("max_file_size_mb") or 10,
                "instructions": payload.get("instructions"),
            })

    fee_rule = get_fee_rule(context)
    if fee_rule:
        fee = fee_rule.amount
        currency = fee_rule.currency

    return {
        "service": service,
        "service_name": service_doc.service_name,
        "eligibility": eligibility,
        "fee": fee,
        "currency": currency,
        "processing_time": service_doc.default_processing_time,
        "requires_appointment": appointment_required,
        "required_documents": requirements,
        "notices": notices,
        "instructions": service_doc.service_instructions,
    }


def get_fee_rule(context):
    filters = {
        "service": context.get("service"),
        "processing_type": context.get("processing_type") or "Normal",
        "active": 1,
    }
    candidates = frappe.get_all(
        "Consular Fee Rule",
        filters=filters,
        fields=["name", "nationality", "residence_country", "visa_type", "entry_type", "amount", "currency"],
        order_by="effective_from desc, modified desc",
    )
    for row in candidates:
        if row.nationality and row.nationality != context.get("nationality"):
            continue
        if row.residence_country and row.residence_country != context.get("residence_country"):
            continue
        if row.visa_type and row.visa_type != context.get("visa_type"):
            continue
        if row.entry_type and row.entry_type != context.get("entry_type"):
            continue
        return row
    return None
