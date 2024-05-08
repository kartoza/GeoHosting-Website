import frappe
import json
from frappe import _

def get_context(context):
    try:
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
            "country": user_profile.institution_country,
            "user_avatar": user_profile.user_avatar
        }

        context.user_profile = json.dumps(user_profile_data)
    except frappe.exceptions.DoesNotExistError:
        # If UserProfile doesn't exist for the user
        context.create_profile_prompt = True

    return context


@frappe.whitelist()
def update_user_profile(data):
    data = frappe.parse_json(data)

    user_profile = frappe.get_doc("UserProfile", {"email": frappe.session.user})

    user_profile.update({
        "name": data.get("name"),
        "surname": data.get("surname"),
        "email": data.get("email"),
        "phone_number": data.get("phone"),
        "institution_name": data.get("institution"),
        "institution_city": data.get("city"),
        "institution_region": data.get("region"),
        "institution_address": data.get("address"),
        "institution_postal_code": data.get("postal"),
        "institution_country": data.get("country")
    })

    user_profile.save()

    return _("User profile updated successfully.")