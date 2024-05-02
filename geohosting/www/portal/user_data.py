import frappe

#TODO THIS SHOULD BE USED TO RETRIEVE USER DATA EG PROFILE, INVOICES ,PRODUCTS ETC

def get_user_profile(user_id):
    # Query user profile based on user ID
    user_profile = frappe.get_doc("User Profile", {"user": user_id})
    
    # Retrieve profile data
    profile_data = {
        "full_name": user_profile.full_name,
        "email": user_profile.email,
        # Add more fields as needed
    }
    
    return profile_data

# Example usage: Get profile for logged-in user
def get_logged_in_user_profile():
    # Get logged-in user ID from session or context
    user_id = frappe.session.user
    
    # Retrieve user profile
    profile_data = get_user_profile(user_id)
    
    return profile_data



# Example usage: update profile for logged-in user
@frappe.whitelist()
def update_user_profile(full_name, email):
    # Get current user
    user_id = frappe.session.user

    # Update user profile
    user_profile = frappe.get_doc("User Profile", {"user": user_id})
    user_profile.full_name = full_name
    user_profile.email = email
    # Update more fields as needed
    user_profile.save()

    return "Profile updated successfully"
