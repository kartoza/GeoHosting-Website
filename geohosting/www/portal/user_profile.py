import frappe
import json

def get_context(context):
    try:
        # Try to fetch user profile data for the logged-in user
        user_profile = frappe.get_doc("UserProfile", {"email": frappe.session.user})

        # Create a dictionary containing only the necessary fields
        user_profile_data = {
            "first_name": user_profile.first_name,
            "last_name": user_profile.last_name,
            "email": user_profile.email,
            "phone": user_profile.phone_number,
            "institution": user_profile.institution_name,
            "city": user_profile.institution_city,
            "region": user_profile.institution_region,
            "address": user_profile.institution_address,
            "postal": user_profile.institution_postal_code,
            "country": user_profile.institution_country
        }

        # Convert the dictionary to JSON and add it to the context
        context.user_profile = json.dumps(user_profile_data)
    except frappe.exceptions.DoesNotExistError:
        # If UserProfile doesn't exist for the user, prompt to create a new profile
        context.create_profile_prompt = True

    return context
