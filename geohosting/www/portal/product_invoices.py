import frappe

from datetime import datetime, date, timedelta

def serialize_datetime(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, timedelta):
        # Convert timedelta to seconds for serialization
        return obj.total_seconds()
    return obj

# TODO IF ADMIN RETRIEVE ALL INVOICES
def get_context(context):
    user_invoices = frappe.db.get_all("Sales Invoice", filters={
        'owner': ['=', frappe.session.user],
    }, fields='*', order_by="name")
    
    # Serialize datetime objects in invoices
    for invoice in user_invoices:
        for key, value in invoice.items():
            if isinstance(value, (datetime, date, timedelta)):
                invoice[key] = serialize_datetime(value)

    context.invoices = user_invoices
    

    return context
