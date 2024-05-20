import frappe
import json
from frappe import _
from jinja2.runtime import DebugUndefined

def get_context(context):
    try:
        user = frappe.session.user
        primary_address = get_customer_address(user)
        create_address_prompt = not bool(primary_address)

        user_doc = frappe.get_doc("User", user)

        # Initialize user profile data with user-related information
        user_profile_data = {
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

        # Check for DebugUndefined and replace with None or a default value
        for key, value in user_profile_data.items():
            if isinstance(value, DebugUndefined):
                user_profile_data[key] = None
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, DebugUndefined):
                        user_profile_data[key][sub_key] = None

        try:
            # Fetch customer data if available
            customer = frappe.get_all("Customer", filters={"account_manager": user}, fields=['*'], limit=1)
            if customer:
                user_profile_data["customer_name"] = customer[0].get("customer_name", "")
        except frappe.DoesNotExistError:
            frappe.log_error(title="Customer Doctype Missing", message="Customer doctype does not exist.")
        except Exception as e:
            frappe.log_error(title="Error fetching customer data", message=str(e))

        # Log the content before serialization for debugging
        log_message = f"user_profile_data: {user_profile_data}"
        frappe.log_error(title="User profile data fetched", message=log_message)

        # Serialize the user profile data to JSON
        context.user_profile = json.dumps(user_profile_data)

    except Exception as e:
        log_message = f"Error fetching user profile: {str(e)}"
        frappe.log_error(title="Error fetching user profile", message=log_message)
        context.error_message = "Error fetching user profile"

    return context

def get_customer_address(customer_name):
    # Query the address linked to the customer
    primary_address = frappe.get_all("Address",
                                     filters={"owner": customer_name, "is_primary_address": 1},
                                     fields=["name", "address_title", "address_line1", "city", "country", "pincode", "state"])

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
