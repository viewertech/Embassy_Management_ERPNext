import frappe


def execute():
    if frappe.db.exists("Workflow", "EMS - Generic Consular Application Workflow"):
        return
    workflow = frappe.new_doc("Workflow")
    workflow.workflow_name = "EMS - Generic Consular Application Workflow"
    workflow.document_type = "Consular Application"
    workflow.workflow_state_field = "application_status"
    workflow.is_active = 0
    states = [
        "Draft", "Submitted", "Payment Review", "Appointment Review", "Document Review",
        "Officer Review", "Supervisor Approval", "Final Decision", "Completed",
    ]
    for state in states:
        workflow.append("states", {"state": state, "doc_status": 0, "allow_edit": "Embassy Administrator"})
    transitions = [
        ("Submit", "Draft", "Submitted", "Applicant"),
        ("Start Payment Review", "Submitted", "Payment Review", "Cashier / Finance Officer"),
        ("Start Appointment Review", "Payment Review", "Appointment Review", "Appointment Officer"),
        ("Start Document Review", "Appointment Review", "Document Review", "Consular Officer"),
        ("Start Officer Review", "Document Review", "Officer Review", "Consular Officer"),
        ("Escalate", "Officer Review", "Supervisor Approval", "Consular Officer"),
        ("Approve", "Supervisor Approval", "Final Decision", "Head of Consular Section"),
        ("Complete", "Final Decision", "Completed", "Consular Officer"),
    ]
    for action, state, next_state, role in transitions:
        workflow.append("transitions", {"action": action, "state": state, "next_state": next_state, "allowed": role})
    workflow.insert(ignore_permissions=True)
