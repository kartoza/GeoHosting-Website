import frappe
import json
from frappe import _

def get_context(context):
    try:
        customer = frappe.get_all("Customer", filters={"account_manager": frappe.session.user}, fields=['*'], limit=1)


        if customer:
            user = frappe.session.user
            primary_address = get_customer_address(user)
            create_address_prompt = not bool(primary_address)

            user_doc = frappe.get_doc("User", user)

            # Create user profile data
            user_profile_data = {
                "customer_name": customer[0]["customer_name"],
                "first_name": user_doc.first_name,
                "last_name": user_doc.last_name,
                "contact_info": {
                    "email": user_doc.email,
                    "mobile_no": user_doc.mobile_no,
                },
                "address_info": primary_address,
                "customer_avatar": user_doc.user_image,
                "create_address_prompt": create_address_prompt
            }
        
            context.user_profile = json.dumps(user_profile_data)

        else:
            context.create_customer_prompt = True


        
        
    except Exception as e:
        frappe.log_error(f"Error fetching user profile: {str(e)}")
        context.error_message = "Error fetching user profile"

    return context


def get_customer_address(customer_name):
    # Query the address linked to the customer
    primary_address = frappe.get_all("Address",
                                     filters={"owner": customer_name, "is_primary_address": 1},
                                     fields=["name", "address_title","address_line1", "city", "country", "pincode", "state"])

    if primary_address:
        # Return the primary address as a dictionary
        return {
            "name": primary_address[0]["name"],
            "address_title": primary_address[0]["address_title"],
            "address_line1": primary_address[0]["address_line1"],
            "city": primary_address[0]["city"],
            "country": primary_address[0]["country"],
            "pincode": primary_address[0]["pincode"],
            "state": primary_address[0]["state"]
        }
    else:
        return {}


