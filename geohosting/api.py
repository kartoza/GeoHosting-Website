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

