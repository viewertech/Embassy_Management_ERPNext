from __future__ import annotations

import base64
from itertools import cycle

import frappe
from frappe.utils import add_days, now, today
from frappe.utils.file_manager import save_file

from embassy_management.setup import ensure_roles, import_sample_data


DEMO_PREFIX = "EMSDEMO"
LEGACY_SERVICE_CODES = ("GEN-VISA", "GEN-PASSPORT", "GEN-CARD", "GEN-ATTEST")
DEMO_SERVICE_CODES = (
    "EMSDEMO-VISA-TOURIST",
    "EMSDEMO-VISA-BUSINESS",
    "EMSDEMO-PASSPORT-RENEWAL",
    "EMSDEMO-CONSULAR-CARD",
    "EMSDEMO-ATTESTATION",
    "EMSDEMO-ETD",
    "EMSDEMO-CIVIL-REGISTRY",
)
SAMPLE_SERVICE_CODES = LEGACY_SERVICE_CODES + DEMO_SERVICE_CODES
DEMO_LOCATIONS = (
    "EMSDEMO Main Consular Counter",
    "EMSDEMO Visa Interview Room",
    "EMSDEMO Biometrics Desk",
)
DEMO_USERS = tuple(f"emsdemo.applicant{i:02d}@example.invalid" for i in range(1, 17))
DEMO_OFFICERS = (
    "emsdemo.consular.officer@example.invalid",
    "emsdemo.visa.officer@example.invalid",
    "emsdemo.appointment.officer@example.invalid",
    "emsdemo.finance.officer@example.invalid",
    "emsdemo.supervisor@example.invalid",
)

PDF_BYTES = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n"
PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


def load_sample_data():
    clear_sample_data()
    ensure_roles()
    import_sample_data()
    _create_erpnext_demo_masters()
    _create_ems_presentation_data()
    frappe.db.commit()
    return "EMSDEMO presentation data loaded."


def clear_sample_data():
    app_names = _demo_application_names()

    _delete_linked_application_records(app_names)
    _delete_demo_records("Communication", {"reference_doctype": "Consular Application", "reference_name": ["in", app_names]})
    _delete_demo_records("ToDo", {"reference_type": "Consular Application", "reference_name": ["in", app_names]})
    _delete_demo_records("File", {"file_name": ["like", f"{DEMO_PREFIX}-%"]})

    for doctype in (
        "Visa Application Details",
        "Passport Service Details",
        "Consular Card Details",
        "Attestation Legalisation Details",
        "Emergency Travel Document Details",
        "Civil Registry Details",
    ):
        _delete_demo_records(doctype, {"consular_application": ["in", app_names]})

    _delete_demo_records("Consular Application", {"name": ["in", app_names]})
    _delete_demo_records("Embassy Applicant Profile", {"email": ["like", "emsdemo.%@example.invalid"]})

    for doctype, prefix_field in (
        ("Embassy Appointment", "booking_code"),
        ("Appointment Slot", None),
        ("Appointment Service Type", "service_type_name"),
        ("Appointment Location", "location_name"),
        ("Consular Payment Review", None),
        ("Consular Fee Waiver", None),
        ("Consular Fee Rule", None),
        ("Consular Service", "service_code"),
    ):
        if prefix_field:
            _delete_demo_records(doctype, {prefix_field: ["like", f"{DEMO_PREFIX}%"]})

    _delete_demo_records("Consular Payment Review", {"application": ["in", app_names]})
    _delete_demo_records("Consular Fee Rule", {"service": ["in", SAMPLE_SERVICE_CODES]})
    _delete_demo_records("Consular Service Document Requirement", {"parent": ["in", SAMPLE_SERVICE_CODES]})
    _delete_demo_records("Appointment Slot", {"service": ["in", SAMPLE_SERVICE_CODES]})
    _delete_demo_records("Embassy Appointment", {"service": ["in", SAMPLE_SERVICE_CODES]})

    for code in SAMPLE_SERVICE_CODES:
        if _exists("Consular Service", code):
            frappe.delete_doc("Consular Service", code, force=True, ignore_permissions=True)

    _clear_erpnext_demo_masters()
    _delete_demo_users()
    frappe.db.commit()
    return "EMSDEMO presentation data cleared."


def _create_erpnext_demo_masters():
    _ensure_item_group("EMSDEMO Consular Services")
    _ensure_supplier_group("EMSDEMO Suppliers")

    for item_code, item_name, rate in (
        ("EMSDEMO-ITEM-VISA-TOURIST", "EMSDEMO Tourist Visa Fee", 100),
        ("EMSDEMO-ITEM-VISA-BUSINESS", "EMSDEMO Business Visa Fee", 150),
        ("EMSDEMO-ITEM-PASSPORT", "EMSDEMO Passport Service Fee", 80),
        ("EMSDEMO-ITEM-CARD", "EMSDEMO Consular Card Fee", 50),
        ("EMSDEMO-ITEM-ATTEST", "EMSDEMO Attestation Fee", 40),
        ("EMSDEMO-ITEM-ETD", "EMSDEMO Emergency Travel Document Fee", 65),
        ("EMSDEMO-ITEM-CIVIL", "EMSDEMO Civil Registry Fee", 35),
        ("EMSDEMO-ITEM-COURIER", "EMSDEMO Secure Courier Fee", 20),
        ("EMSDEMO-ITEM-SMS", "EMSDEMO SMS Notification Fee", 5),
        ("EMSDEMO-ITEM-FASTTRACK", "EMSDEMO Fast Track Surcharge", 75),
    ):
        _upsert_doc(
            "Item",
            item_code,
            {
                "item_code": item_code,
                "item_name": item_name,
                "item_group": _first_existing("Item Group", "EMSDEMO Consular Services", "Services", "All Item Groups"),
                "stock_uom": _first_existing("UOM", "Nos", "Unit"),
                "is_stock_item": 0,
                "is_sales_item": 1,
                "is_purchase_item": 0,
                "standard_rate": rate,
                "description": f"{item_name}. Presentation data only. Powered by Viewertech.",
            },
        )

    for supplier in ("Print Partner", "Courier Partner", "Biometrics Partner", "Translation Partner", "Payment Partner"):
        _upsert_doc(
            "Supplier",
            f"EMSDEMO {supplier}",
            {
                "supplier_name": f"EMSDEMO {supplier}",
                "supplier_group": _first_existing("Supplier Group", "EMSDEMO Suppliers", "Services", "All Supplier Groups"),
                "supplier_type": "Company",
            },
        )

    for lead_index, company in enumerate(("Global Study Ltd", "Atlas Minerals", "Civic Records Office"), 1):
        _upsert_doc(
            "Lead",
            f"EMSDEMO-LEAD-{lead_index:02d}",
            {
                "lead_name": f"EMSDEMO {company}",
                "company_name": f"EMSDEMO {company}",
                "email_id": f"emsdemo.lead{lead_index:02d}@example.invalid",
                "status": "Open",
                "source": "Website",
            },
        )


def _create_ems_presentation_data():
    services = _create_services()
    _create_locations_and_slots(services)
    applicants = _create_applicants()
    _create_erpnext_operational_records(applicants)
    _create_applications(applicants, services)


def _create_services():
    service_rows = (
        ("EMSDEMO-VISA-TOURIST", "Tourist Visa", "Visa", "EMSDEMO-ITEM-VISA-TOURIST", 100, "5 working days"),
        ("EMSDEMO-VISA-BUSINESS", "Business Visa", "Visa", "EMSDEMO-ITEM-VISA-BUSINESS", 150, "5 working days"),
        ("EMSDEMO-PASSPORT-RENEWAL", "Passport Renewal", "Passport", "EMSDEMO-ITEM-PASSPORT", 80, "10 working days"),
        ("EMSDEMO-CONSULAR-CARD", "Consular Card", "Consular Card", "EMSDEMO-ITEM-CARD", 50, "7 working days"),
        ("EMSDEMO-ATTESTATION", "Document Attestation", "Attestation", "EMSDEMO-ITEM-ATTEST", 40, "3 working days"),
        ("EMSDEMO-ETD", "Emergency Travel Document", "Emergency Travel Document", "EMSDEMO-ITEM-ETD", 65, "1 working day"),
        ("EMSDEMO-CIVIL-REGISTRY", "Civil Registry Request", "Civil Registry", "EMSDEMO-ITEM-CIVIL", 35, "8 working days"),
    )
    services = {}
    for code, label, category, item, fee, processing_time in service_rows:
        doc = _upsert_doc(
            "Consular Service",
            code,
            {
                "service_code": code,
                "service_name": f"EMSDEMO {label}",
                "service_category": category,
                "description": f"Generic presentation service for {label.lower()}. Not official government data.",
                "enabled_on_public_portal": 1,
                "requires_appointment": 1 if category in ("Visa", "Passport", "Consular Card", "Emergency Travel Document") else 0,
                "requires_online_application": 1,
                "requires_document_upload": 1,
                "requires_payment": 1,
                "requires_officer_review": 1,
                "requires_biometrics": 1 if category in ("Passport", "Emergency Travel Document") else 0,
                "requires_interview": 1 if category == "Visa" else 0,
                "default_processing_time": processing_time,
                "fee_item": item if _exists("Item", item) else None,
                "default_fee": fee,
                "currency": "USD",
                "validity_period": "Configurable per policy",
                "service_instructions": "Presentation data only. Configure real mission instructions before production.",
                "eligibility_rules": "Rule-based eligibility can be configured per service, nationality, residence, and visa type.",
                "terms_and_declaration": "I confirm the information supplied is accurate. Powered by Viewertech.",
            },
        )
        doc.required_documents = []
        for sequence, category_label in enumerate(_documents_for_service(category), 1):
            doc.append(
                "required_documents",
                {
                    "document_category": category_label,
                    "requirement_label": f"{category_label} - {label}",
                    "mandatory": 1,
                    "allowed_file_types": "pdf,jpg,jpeg,png",
                    "max_file_size_mb": 10,
                    "instructions": "Upload a clear copy for officer review.",
                    "sequence": sequence,
                },
            )
        doc.save(ignore_permissions=True)
        services[code] = doc
        _create_fee_rules(code, item, fee)
    return services


def _create_fee_rules(service, item, fee):
    variants = (
        ("Normal", "", fee),
        ("Fast Track", "", fee + 75),
        ("Emergency", "", fee + 120),
    )
    if "VISA" in service:
        variants = (
            ("Normal", "Single", fee),
            ("Normal", "Multiple", fee + 50),
            ("Fast Track", "Single", fee + 75),
            ("Emergency", "Single", fee + 120),
        )
    for processing_type, entry_type, amount in variants:
        _insert_if_missing(
            "Consular Fee Rule",
            {
                "service": service,
                "visa_type": "Business" if "BUSINESS" in service else ("Tourist" if "VISA" in service else ""),
                "processing_type": processing_type,
                "entry_type": entry_type,
                "fee_item": item if _exists("Item", item) else None,
                "amount": amount,
                "currency": "USD",
                "effective_from": today(),
                "active": 1,
            },
            {
                "service": service,
                "processing_type": processing_type,
                "entry_type": entry_type,
                "amount": amount,
            },
        )


def _create_locations_and_slots(services):
    for idx, location in enumerate(DEMO_LOCATIONS, 1):
        _upsert_doc(
            "Appointment Location",
            location,
            {
                "location_name": location,
                "time_zone": "Etc/UTC",
                "room_counter": f"Counter {idx}",
                "active": 1,
            },
        )

    for service in services:
        service_type = f"{service} Appointment"
        _upsert_doc(
            "Appointment Service Type",
            service_type,
            {
                "service_type_name": service_type,
                "service": service,
                "duration_minutes": 30,
                "default_capacity": 4,
                "requires_application": 1,
                "enabled": 1,
            },
        )
        for day in range(1, 8):
            for slot_index, start in enumerate(("09:00:00", "10:30:00", "13:30:00"), 1):
                _insert_if_missing(
                    "Appointment Slot",
                    {
                        "service": service,
                        "appointment_service_type": service_type,
                        "location": DEMO_LOCATIONS[(day + slot_index) % len(DEMO_LOCATIONS)],
                        "slot_date": add_days(today(), day),
                        "from_time": start,
                        "to_time": _slot_end(start),
                        "capacity": 4,
                        "booked_count": 0,
                        "active": 1,
                        "exclude_public_holiday": 1,
                    },
                    {"service": service, "slot_date": add_days(today(), day), "from_time": start},
                )


def _create_applicants():
    countries = cycle(["United States", "United Kingdom", "Canada", "France", "Portugal", "Spain"])
    people = (
        ("Amina", "Hart"),
        ("Jonas", "Mercer"),
        ("Lina", "Okafor"),
        ("Mateo", "Silva"),
        ("Nora", "Bennett"),
        ("Theo", "Rahman"),
        ("Elena", "Costa"),
        ("Samuel", "Wright"),
        ("Maya", "Dupont"),
        ("Owen", "Patel"),
        ("Rosa", "King"),
        ("Ibrahim", "Cole"),
        ("Sofia", "Grant"),
        ("Daniel", "Morgan"),
        ("Layla", "Scott"),
        ("Noah", "Foster"),
    )
    applicants = []
    for idx, (first_name, last_name) in enumerate(people, 1):
        email = f"emsdemo.applicant{idx:02d}@example.invalid"
        user = _ensure_user(email, first_name, last_name, ["Applicant"])
        customer = _upsert_doc(
            "Customer",
            f"EMSDEMO-CUSTOMER-{idx:02d}",
            {
                "customer_name": f"EMSDEMO {first_name} {last_name}",
                "customer_type": "Individual",
                "customer_group": _first_existing("Customer Group", "Individual", "All Customer Groups"),
                "territory": _first_existing("Territory", "All Territories"),
            },
        )
        contact = _upsert_contact(idx, first_name, last_name, email, customer.name)
        address = _upsert_address(idx, first_name, last_name, next(countries), customer.name)
        profile = _upsert_doc(
            "Embassy Applicant Profile",
            f"EMSDEMO-APPLICANT-{idx:02d}",
            {
                "user": user.name,
                "customer": customer.name,
                "contact": contact.name,
                "address": address.name,
                "full_name": f"{first_name} {last_name}",
                "date_of_birth": add_days(today(), -9000 - idx * 150),
                "nationality": _country(next(countries)),
                "residence_country": _country("United Kingdom"),
                "preferred_language": _first_existing("Language", "en", "English"),
                "mobile_no": f"+44 7700 90{idx:04d}",
                "email": email,
                "data_consent": 1,
                "consent_logged_on": now(),
            },
        )
        applicants.append(profile)
    return applicants


def _create_applications(applicants, services):
    service_cycle = cycle(DEMO_SERVICE_CODES)
    statuses = (
        "Draft",
        "Submitted",
        "Payment Pending",
        "Payment Confirmed",
        "Appointment Required",
        "Appointment Booked",
        "Under Initial Review",
        "Awaiting Additional Documents",
        "Awaiting Interview",
        "Under Officer Review",
        "Approved",
        "Rejected",
        "Completed",
        "Collected / Dispatched",
        "Under Officer Review",
        "Payment Confirmed",
    )
    for idx, applicant in enumerate(applicants, 1):
        service = next(service_cycle)
        status = statuses[idx - 1]
        application_number = f"{DEMO_PREFIX}-APP-{idx:03d}"
        app = _insert_if_missing(
            "Consular Application",
            {
                "application_number": application_number,
                "applicant": applicant.name,
                "customer": applicant.customer,
                "contact": applicant.contact,
                "service": service,
                "embassy_mission": "Generic Embassy Presentation Mission",
                "application_status": status,
                "priority": "Emergency" if idx in (6, 15) else ("Urgent" if idx in (4, 9, 12) else "Normal"),
                "submission_channel": ["Online", "Walk-in", "Postal", "Agent"][idx % 4],
                "total_fee": _service_fee(service),
                "currency": "USD",
                "payment_status": _payment_status_for(status),
                "assigned_officer": "Administrator",
                "review_status": _review_status_for(status),
                "decision": "Approved" if status in ("Approved", "Completed", "Collected / Dispatched") else ("Rejected" if status == "Rejected" else ""),
                "rejection_reason": "Presentation rejection reason: missing original document." if status == "Rejected" else "",
                "internal_notes": f"{DEMO_PREFIX}: presentation case for officer workbench, reporting, and dashboards.",
                "applicant_notes": "Presentation data only. Not official government data.",
                "submitted_on": now() if status != "Draft" else None,
                "progress_percent": _progress_for(status),
                "declaration_accepted": 1 if status != "Draft" else 0,
                "privacy_consent": 1,
                "terms_accepted": 1 if status != "Draft" else 0,
                "locked_after_submission": 1 if status != "Draft" else 0,
            },
            {"application_number": application_number},
        )
        _create_service_details(app, service, idx)
        _create_application_documents(app, service, idx)
        _create_application_appointment(app, applicant, service, idx, status)
        _create_payment_review(app, idx, status)
        _create_todo_and_communication(app, idx, status)


def _create_service_details(app, service, idx):
    if "VISA" in service:
        _insert_if_missing(
            "Visa Application Details",
            {
                "consular_application": app.name,
                "visa_type": "Business" if "BUSINESS" in service else "Tourist",
                "entry_type": "Multiple" if "BUSINESS" in service else "Single",
                "purpose_of_travel": "Presentation itinerary for demo review.",
                "intended_date_of_entry": add_days(today(), 20 + idx),
                "intended_date_of_exit": add_days(today(), 35 + idx),
                "point_of_entry": "International Airport",
                "point_of_exit": "International Airport",
                "host_sponsor": "EMSDEMO Host Organisation",
                "host_address": "Presentation host address",
                "ticket_reference": f"EMS-TKT-{idx:04d}",
                "ticket_issued_by": "EMSDEMO Travel Desk",
                "previous_visits": "None declared" if idx % 2 else "One previous visit declared",
                "previous_visa_refusals": "None",
                "invitation_letter_required": 1 if "BUSINESS" in service else 0,
                "yellow_fever_certificate_required": 1,
                "travel_itinerary_required": 1,
                "hotel_booking_required": 1,
                "employment_letter_required": 1 if "BUSINESS" in service else 0,
            },
            {"consular_application": app.name},
        )
    elif "PASSPORT" in service:
        _insert_if_missing(
            "Passport Service Details",
            {
                "consular_application": app.name,
                "passport_type": "Ordinary",
                "passport_number": f"P{idx:07d}",
                "issue_date": add_days(today(), -1800),
                "expiry_date": add_days(today(), 180),
                "place_of_issue": "Generic Issuing Authority",
                "service_request_type": "Renewal",
                "biometric_appointment_required": 1,
            },
            {"consular_application": app.name},
        )
    elif "CARD" in service:
        _insert_if_missing(
            "Consular Card Details",
            {
                "consular_application": app.name,
                "current_nationality": _country("United States"),
                "nationality_at_birth": _country("United States"),
                "place_of_birth": "Presentation City",
                "parent_details": "Presentation parent details.",
                "diaspora_registration_number": f"EMS-DIAS-{idx:04d}",
                "card_validity": "5 years",
            },
            {"consular_application": app.name},
        )
    elif "ATTESTATION" in service:
        _insert_if_missing(
            "Attestation Legalisation Details",
            {
                "consular_application": app.name,
                "document_type": "Degree Certificate",
                "document_owner": app.applicant,
                "issuing_authority": "Presentation University",
                "country_of_issue": _country("United Kingdom"),
                "legalisation_type": "Attestation",
                "number_of_copies": 2,
                "original_document_verified": 1 if idx % 2 == 0 else 0,
            },
            {"consular_application": app.name},
        )
    elif "ETD" in service:
        _insert_if_missing(
            "Emergency Travel Document Details",
            {
                "consular_application": app.name,
                "reason": "Lost Passport",
                "destination_country": _country("United States"),
                "travel_date": add_days(today(), 3),
                "valid_until": add_days(today(), 30),
            },
            {"consular_application": app.name},
        )
    elif "CIVIL" in service:
        _insert_if_missing(
            "Civil Registry Details",
            {
                "consular_application": app.name,
                "registry_service_type": "Birth Registration",
                "event_date": add_days(today(), -120),
                "event_country": _country("United Kingdom"),
                "related_person": "Presentation dependent",
                "certificate_required": 1,
                "number_of_copies": 1,
            },
            {"consular_application": app.name},
        )


def _create_application_documents(app, service, idx):
    categories = _documents_for_service(_service_category(service))[:3]
    statuses = cycle(["Accepted", "Uploaded", "Unclear", "Re-upload Requested"])
    for sequence, category in enumerate(categories, 1):
        req = _insert_if_missing(
            "Application Document Requirement",
            {
                "application": app.name,
                "service": service,
                "document_category": category,
                "requirement_label": f"{category} for {app.application_number}",
                "mandatory": 1,
                "allowed_file_types": "pdf,jpg,jpeg,png",
                "max_file_size_mb": 10,
                "instructions": "Presentation document requirement.",
                "sequence": sequence,
            },
            {"application": app.name, "document_category": category, "requirement_label": f"{category} for {app.application_number}"},
        )
        file_doc = _save_demo_file(app, category, sequence)
        status = next(statuses)
        _insert_if_missing(
            "Application Uploaded Document",
            {
                "application": app.name,
                "requirement": req.name,
                "document_category": category,
                "file": file_doc.name,
                "status": status,
                "review_notes": f"{DEMO_PREFIX}: {status.lower()} during presentation review.",
                "reviewed_by": "Administrator" if status != "Uploaded" else None,
                "reviewed_on": now() if status != "Uploaded" else None,
                "reupload_requested": 1 if status == "Re-upload Requested" else 0,
            },
            {"application": app.name, "document_category": category, "file": file_doc.name},
        )


def _create_application_appointment(app, applicant, service, idx, status):
    if status in ("Draft", "Submitted", "Payment Pending"):
        return
    booking_code = f"{DEMO_PREFIX}-BOOK-{idx:03d}"
    appointment = _insert_if_missing(
        "Embassy Appointment",
        {
            "booking_code": booking_code,
            "application": app.name,
            "applicant": applicant.name,
            "service": service,
            "appointment_service_type": f"{service} Appointment",
            "location": DEMO_LOCATIONS[idx % len(DEMO_LOCATIONS)],
            "officer": "Administrator",
            "appointment_date": add_days(today(), idx % 9 + 1),
            "start_time": ["09:00:00", "10:30:00", "13:30:00"][idx % 3],
            "end_time": ["09:30:00", "11:00:00", "14:00:00"][idx % 3],
            "status": "Completed" if status in ("Approved", "Completed", "Collected / Dispatched") else "Confirmed",
            "external_appointment_reference": f"EXT-{booking_code}",
            "queue_number": f"Q{idx:03d}",
            "notes": f"{DEMO_PREFIX}: appointment presentation record.",
        },
        {"booking_code": booking_code},
    )
    if app.appointment != appointment.name:
        app.appointment = appointment.name
        app.booking_code = booking_code
        app.save(ignore_permissions=True)


def _create_payment_review(app, idx, status):
    if app.payment_status == "Not Required":
        return
    _insert_if_missing(
        "Consular Payment Review",
        {
            "application": app.name,
            "amount": app.total_fee,
            "currency": app.currency,
            "review_status": "Confirmed" if app.payment_status == "Payment Confirmed" else "Pending",
            "reviewed_by": "Administrator" if app.payment_status == "Payment Confirmed" else None,
            "reviewed_on": now() if app.payment_status == "Payment Confirmed" else None,
            "review_notes": f"{DEMO_PREFIX}: bank transfer proof review for presentation.",
        },
        {"application": app.name, "amount": app.total_fee},
    )


def _create_todo_and_communication(app, idx, status):
    _insert_if_missing(
        "ToDo",
        {
            "allocated_to": "Administrator",
            "reference_type": "Consular Application",
            "reference_name": app.name,
            "description": f"{DEMO_PREFIX}: Review {app.application_number} ({status}).",
            "status": "Open" if status not in ("Approved", "Rejected", "Completed", "Collected / Dispatched") else "Closed",
            "priority": "High" if app.priority in ("Urgent", "Emergency") else "Medium",
            "date": add_days(today(), idx % 5),
        },
        {"reference_type": "Consular Application", "reference_name": app.name, "description": ["like", f"{DEMO_PREFIX}%"]},
    )
    _insert_if_missing(
        "Communication",
        {
            "communication_type": "Communication",
            "communication_medium": "Email",
            "sent_or_received": "Received",
            "subject": f"{DEMO_PREFIX}: Applicant message for {app.application_number}",
            "content": "Presentation applicant message for the officer review timeline. Powered by Viewertech.",
            "sender": f"emsdemo.applicant{idx:02d}@example.invalid",
            "recipients": "consular@example.invalid",
            "reference_doctype": "Consular Application",
            "reference_name": app.name,
        },
        {"reference_doctype": "Consular Application", "reference_name": app.name, "subject": ["like", f"{DEMO_PREFIX}%"]},
    )


def _save_demo_file(app, category, sequence):
    extension = "png" if category == "Photo" else "pdf"
    file_name = f"{DEMO_PREFIX}-{app.application_number}-{sequence}-{frappe.scrub(category)}.{extension}"
    existing = frappe.db.exists("File", {"file_name": file_name})
    if existing:
        return frappe.get_doc("File", existing)
    content = PNG_BYTES if extension == "png" else PDF_BYTES
    return save_file(file_name, content, "Consular Application", app.name, folder="Home/Attachments", is_private=1)


def _delete_linked_application_records(app_names):
    if not app_names:
        return
    for doctype in ("Application Uploaded Document", "Application Document Requirement", "Embassy Appointment", "Consular Payment Review"):
        _delete_demo_records(doctype, {"application": ["in", app_names]})


def _clear_erpnext_demo_masters():
    for doctype, filters in (
        ("Task", {"name": ["like", f"{DEMO_PREFIX}-%"]}),
        ("Project", {"name": ["like", f"{DEMO_PREFIX}-%"]}),
        ("Lead", {"name": ["like", f"{DEMO_PREFIX}-%"]}),
        ("Lead", {"lead_name": ["like", f"{DEMO_PREFIX}%"]}),
        ("Address", {"name": ["like", f"{DEMO_PREFIX}-%"]}),
        ("Contact", {"name": ["like", f"{DEMO_PREFIX}-%"]}),
        ("Customer", {"name": ["like", f"{DEMO_PREFIX}-%"]}),
        ("Customer", {"customer_name": ["like", f"{DEMO_PREFIX}%"]}),
        ("Supplier", {"name": ["like", f"{DEMO_PREFIX}%"]}),
        ("Supplier", {"supplier_name": ["like", f"{DEMO_PREFIX}%"]}),
        ("Item", {"name": ["like", f"{DEMO_PREFIX}-%"]}),
        ("Item Group", {"name": "EMSDEMO Consular Services"}),
        ("Supplier Group", {"name": "EMSDEMO Suppliers"}),
    ):
        _delete_demo_records(doctype, filters)


def _delete_demo_users():
    for user in DEMO_USERS + DEMO_OFFICERS:
        if _exists("User", user):
            frappe.delete_doc("User", user, force=True, ignore_permissions=True)


def _create_erpnext_operational_records(applicants):
    for idx, profile in enumerate(applicants[:4], 1):
        project = _upsert_doc(
            "Project",
            f"EMSDEMO-PROJECT-{idx:02d}",
            {
                "project_name": f"EMSDEMO Consular Outreach {idx:02d}",
                "status": "Open",
                "customer": profile.customer,
                "expected_start_date": today(),
                "expected_end_date": add_days(today(), 30 + idx),
                "percent_complete": 25 * (idx - 1),
                "notes": "Presentation ERPNext project linked to EMS demo data.",
            },
        )
        if project:
            for task_idx, subject in enumerate(("Prepare case file", "Review supporting documents", "Confirm appointment"), 1):
                _upsert_doc(
                    "Task",
                    f"EMSDEMO-TASK-{idx:02d}-{task_idx:02d}",
                    {
                        "subject": f"EMSDEMO {subject}",
                        "project": project.name,
                        "status": "Open" if task_idx < 3 else "Working",
                        "priority": "High" if task_idx == 2 else "Medium",
                        "exp_start_date": today(),
                        "exp_end_date": add_days(today(), task_idx + idx),
                        "description": "Presentation ERPNext task. Powered by Viewertech.",
                    },
                )


def _demo_application_names():
    if not _doctype_exists("Consular Application"):
        return []
    names = set(frappe.get_all("Consular Application", filters={"application_number": ["like", f"{DEMO_PREFIX}-%"]}, pluck="name"))
    names.update(frappe.get_all("Consular Application", filters={"internal_notes": ["like", f"%{DEMO_PREFIX}%"]}, pluck="name"))
    names.update(frappe.get_all("Consular Application", filters={"name": ["like", "GEN-%"]}, pluck="name"))
    return list(names)


def _delete_demo_records(doctype, filters):
    if not _doctype_exists(doctype):
        return
    if _has_empty_in_filter(filters):
        return
    names = frappe.get_all(doctype, filters=filters, pluck="name")
    for name in names:
        frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)


def _upsert_doc(doctype, name, values):
    if not _doctype_exists(doctype):
        return None
    doc = frappe.get_doc(doctype, name) if frappe.db.exists(doctype, name) else frappe.new_doc(doctype)
    if not doc.name:
        doc.name = name
    _apply_values(doc, values)
    doc.flags.ignore_permissions = True
    if doc.is_new():
        doc.insert(ignore_permissions=True)
    else:
        doc.save(ignore_permissions=True)
    return doc


def _insert_if_missing(doctype, values, filters):
    if not _doctype_exists(doctype):
        return None
    existing = frappe.db.exists(doctype, filters)
    if existing:
        return frappe.get_doc(doctype, existing)
    doc = frappe.new_doc(doctype)
    _apply_values(doc, values)
    doc.insert(ignore_permissions=True)
    return doc


def _apply_values(doc, values):
    valid_fields = {df.fieldname for df in doc.meta.fields}
    for key, value in values.items():
        if value is None:
            continue
        if key in valid_fields or key in {"name", "doctype"}:
            doc.set(key, value)


def _upsert_contact(idx, first_name, last_name, email, customer):
    doc = frappe.get_doc("Contact", f"EMSDEMO-CONTACT-{idx:02d}") if _exists("Contact", f"EMSDEMO-CONTACT-{idx:02d}") else frappe.new_doc("Contact")
    doc.name = f"EMSDEMO-CONTACT-{idx:02d}"
    doc.first_name = first_name
    doc.last_name = last_name
    doc.email_ids = []
    doc.phone_nos = []
    doc.links = []
    doc.append("email_ids", {"email_id": email, "is_primary": 1})
    doc.append("phone_nos", {"phone": f"+44 7700 90{idx:04d}", "is_primary_phone": 1})
    doc.append("links", {"link_doctype": "Customer", "link_name": customer})
    if doc.is_new():
        doc.insert(ignore_permissions=True)
    else:
        doc.save(ignore_permissions=True)
    return doc


def _upsert_address(idx, first_name, last_name, country, customer):
    doc = frappe.get_doc("Address", f"EMSDEMO-ADDRESS-{idx:02d}") if _exists("Address", f"EMSDEMO-ADDRESS-{idx:02d}") else frappe.new_doc("Address")
    doc.name = f"EMSDEMO-ADDRESS-{idx:02d}"
    doc.address_title = f"EMSDEMO {first_name} {last_name}"
    doc.address_type = "Billing"
    doc.address_line1 = f"{idx} Presentation Avenue"
    doc.city = "Demo City"
    doc.country = _country(country)
    doc.links = []
    doc.append("links", {"link_doctype": "Customer", "link_name": customer})
    if doc.is_new():
        doc.insert(ignore_permissions=True)
    else:
        doc.save(ignore_permissions=True)
    return doc


def _ensure_user(email, first_name, last_name, roles):
    if _exists("User", email):
        user = frappe.get_doc("User", email)
    else:
        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "enabled": 1,
                "send_welcome_email": 0,
                "user_type": "System User",
            }
        ).insert(ignore_permissions=True)
    for role in roles:
        if _exists("Role", role):
            user.add_roles(role)
    return user


def _ensure_item_group(name):
    if not _doctype_exists("Item Group") or _exists("Item Group", name):
        return
    doc = frappe.new_doc("Item Group")
    doc.item_group_name = name
    doc.parent_item_group = _first_existing("Item Group", "Services", "All Item Groups")
    doc.is_group = 0
    doc.insert(ignore_permissions=True)


def _ensure_supplier_group(name):
    if not _doctype_exists("Supplier Group") or _exists("Supplier Group", name):
        return
    doc = frappe.new_doc("Supplier Group")
    doc.supplier_group_name = name
    doc.parent_supplier_group = _first_existing("Supplier Group", "Services", "All Supplier Groups")
    doc.is_group = 0
    doc.insert(ignore_permissions=True)


def _documents_for_service(category):
    defaults = {
        "Visa": ["Passport", "Photo", "Flight Ticket", "Proof of Address", "Invitation Letter"],
        "Passport": ["Passport", "Photo", "Proof of Address", "Signature"],
        "Consular Card": ["Photo", "Proof of Address", "Other Documents"],
        "Attestation": ["Other Documents", "Proof of Address", "Signature"],
        "Emergency Travel Document": ["Passport", "Photo", "Other Documents"],
        "Civil Registry": ["Other Documents", "Proof of Address"],
    }
    return defaults.get(category, ["Other Documents"])


def _service_category(service):
    if "VISA" in service:
        return "Visa"
    if "PASSPORT" in service:
        return "Passport"
    if "CARD" in service:
        return "Consular Card"
    if "ATTEST" in service:
        return "Attestation"
    if "ETD" in service:
        return "Emergency Travel Document"
    if "CIVIL" in service:
        return "Civil Registry"
    return "Other"


def _service_fee(service):
    fees = {
        "EMSDEMO-VISA-TOURIST": 100,
        "EMSDEMO-VISA-BUSINESS": 150,
        "EMSDEMO-PASSPORT-RENEWAL": 80,
        "EMSDEMO-CONSULAR-CARD": 50,
        "EMSDEMO-ATTESTATION": 40,
        "EMSDEMO-ETD": 65,
        "EMSDEMO-CIVIL-REGISTRY": 35,
    }
    return fees.get(service, 50)


def _payment_status_for(status):
    if status in ("Draft", "Submitted", "Payment Pending"):
        return "Payment Pending"
    if status in ("Rejected", "Cancelled"):
        return "Payment Under Review"
    return "Payment Confirmed"


def _review_status_for(status):
    if status in ("Draft", "Submitted", "Payment Pending", "Payment Confirmed"):
        return "Not Started"
    if status in ("Awaiting Additional Documents",):
        return "Additional Documents Requested"
    if status in ("Under Officer Review", "Awaiting Interview"):
        return "In Progress"
    if status in ("Approved", "Rejected", "Completed", "Collected / Dispatched"):
        return "Ready for Decision"
    return "In Progress"


def _progress_for(status):
    return {
        "Draft": 20,
        "Submitted": 35,
        "Payment Pending": 45,
        "Payment Confirmed": 55,
        "Appointment Required": 60,
        "Appointment Booked": 70,
        "Under Initial Review": 75,
        "Awaiting Additional Documents": 70,
        "Awaiting Interview": 78,
        "Under Officer Review": 85,
        "Approved": 95,
        "Rejected": 100,
        "Completed": 100,
        "Collected / Dispatched": 100,
    }.get(status, 50)


def _slot_end(start):
    return {"09:00:00": "09:30:00", "10:30:00": "11:00:00", "13:30:00": "14:00:00"}.get(start, "09:30:00")


def _country(name):
    return name if _exists("Country", name) else None


def _first_existing(doctype, *names):
    for name in names:
        if name and _exists(doctype, name):
            return name
    return names[-1] if names else None


def _has_empty_in_filter(filters):
    for value in (filters or {}).values():
        if isinstance(value, (list, tuple)) and len(value) == 2 and value[0] == "in" and not value[1]:
            return True
    return False


def _exists(doctype, name):
    return _doctype_exists(doctype) and bool(frappe.db.exists(doctype, name))


def _doctype_exists(doctype):
    return bool(frappe.db.exists("DocType", doctype))
