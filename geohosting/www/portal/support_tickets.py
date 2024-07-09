import frappe

from datetime import datetime, date, timedelta

no_cache = 1

def serialize_datetime(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, timedelta):
        # Convert timedelta to seconds for serialization
        return obj.total_seconds()
    return obj

def get_context(context):

    support_tickets = frappe.db.get_all("Issue", filters={
        'owner': ['=', frappe.session.user],
    }, fields='*') 

    for support_ticket in support_tickets:
        for key, value in support_ticket.items():
            if isinstance(value, (datetime, date, timedelta)):
                support_ticket[key] = serialize_datetime(value)


    context.support_tickets = support_tickets

    return context

@frappe.whitelist(allow_guest=False)
def update_issue(issue_id, raised_by, owner, subject, issue_type, description, status):
    if not frappe.has_permission("Issue", "write"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    issue = frappe.get_doc("Issue", issue_id)
    issue.raised_by = raised_by
    issue.owner = owner
    issue.subject = subject
    issue.issue_type = issue_type
    issue.description = description
    issue.status = status
    issue.save()
    frappe.db.commit()

    return {
        "message": "Issue updated successfully",
        "data": issue
    }
