import frappe
from frappe import _


@frappe.whitelist()
def update_or_create_address(customer_name, address_data):
    # Check if the address exists for the customer
    existing_address = frappe.get_all("Address",
                                      filters={"owner": customer_name, "is_primary_address": 1},
                                      fields=["name","owner"])

    if existing_address:
        existing_address_doc = frappe.get_doc("Address", existing_address[0]["name"])
        existing_address_doc.update(address_data)
        existing_address_doc.save()
        return {"message": _("Address updated successfully.")}
    else:
        # Address does not exist, create it
        address_doc = frappe.new_doc("Address")
        address_doc.update({
            "owner": customer_name,
            **address_data
        })
        address_doc.insert()
        return {"message": _("Address created successfully.")}



@frappe.whitelist(allow_guest=True)
def get_user_info():
    current_user = frappe.session.user

    # Fetch the associated customer
    customer_name = None
    if current_user and current_user != "Guest":
        customer_record = frappe.get_all("Customer", filters={"owner": current_user}, fields=["customer_name"])
        if customer_record:
            customer_name = customer_record[0].customer_name

    return {
        "current_user": current_user,
        "customer_name": customer_name
    }

@frappe.whitelist(allow_guest=True)
def update_sales_order():
    try:
        sales_order = frappe.get_doc('Sales Order', 'SAL-ORD-2024-00019')
        if sales_order:
            if sales_order.docstatus == 0:
                # Update fields
                sales_order.db_set('status', 'Completed')
                sales_order.db_set('per_delivered', 100)
                sales_order.db_set('per_billed', 100)
                
                # Save the document
                sales_order.save(ignore_permissions=True)
                sales_order.submit()
                frappe.db.commit()
        return {'status': 'success', 'message': 'Sales Order updated successfully.'}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Update Sales Order Fields')
        return {'status': 'error', 'message': str(e)}
    


