app_name = "embassy_management"
app_title = "Embassy Management"
app_publisher = "Viewertech"
app_description = "Reusable ERPNext/Frappe Embassy Management System"
app_email = "hello@viewertech.net"
app_license = "MIT"
required_apps = ["frappe", "erpnext"]
app_logo_url = "/assets/embassy_management/img/app_icon.svg"
app_home = "/desk/embassy-management"
after_install = "embassy_management.setup.sync_desktop_integration"
after_migrate = "embassy_management.setup.sync_desktop_integration"

add_to_apps_screen = [
    {
        "name": "embassy_management",
        "logo": "/assets/embassy_management/img/app_icon.svg",
        "title": "Embassy Management",
        "route": "/desk/embassy-management",
    }
]

app_include_css = "/assets/embassy_management/css/embassy.css"
app_include_js = "/assets/embassy_management/js/embassy.js"
web_include_css = "/assets/embassy_management/css/portal.css"
web_include_js = "/assets/embassy_management/js/portal.js"

website_route_rules = [
    {"from_route": "/embassy/<path:app_path>", "to_route": "embassy"},
]

fixtures = [
    {"dt": "Role", "filters": [["role_name", "in", [
        "Applicant", "Consular Officer", "Visa Officer", "Passport Officer",
        "Appointment Officer", "Cashier / Finance Officer", "Consular Supervisor",
        "Head of Consular Section", "Head of Mission", "Embassy Administrator"
    ]]]},
    {"dt": "Email Template", "filters": [["name", "like", "EMS - %"]]},
    {"dt": "Workflow", "filters": [["name", "like", "EMS - %"]]},
    {"dt": "Workspace", "filters": [["name", "in", ["Embassy Management", "Consular Services", "Embassy Finance"]]]},
    {"dt": "Dashboard Chart", "filters": [["name", "like", "EMS - %"]]},
    {"dt": "Number Card", "filters": [["name", "like", "EMS - %"]]},
]

scheduler_events = {
    "daily": [
        "embassy_management.tasks.send_appointment_reminders",
        "embassy_management.tasks.mark_overdue_applications",
    ],
}

permission_query_conditions = {
    "Consular Application": "embassy_management.permissions.get_consular_application_permission_query_conditions",
    "Application Uploaded Document": "embassy_management.permissions.get_uploaded_document_permission_query_conditions",
    "Embassy Appointment": "embassy_management.permissions.get_appointment_permission_query_conditions",
}

has_permission = {
    "Consular Application": "embassy_management.permissions.has_consular_application_permission",
    "Application Uploaded Document": "embassy_management.permissions.has_uploaded_document_permission",
    "Embassy Appointment": "embassy_management.permissions.has_appointment_permission",
}
