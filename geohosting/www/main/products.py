import frappe

def get_context(context):

    products = frappe.db.sql("""SELECT * FROM `tabProducts`;""", as_dict=True)
    context.products = products

    return context