import frappe

from datetime import datetime, date, timedelta

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