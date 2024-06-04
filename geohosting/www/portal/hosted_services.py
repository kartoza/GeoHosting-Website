import frappe

def get_user_products():
    try:
        # Get the current logged-in user
        user = frappe.session.user
        
        # Query User Products for the current user
        user_products = frappe.get_all("User Products", filters={"user": user}, fields=["*"])
        
        return user_products
    except Exception as e:
        frappe.log_error(f"Failed to fetch user products for {user}: {str(e)}")
        return []

def get_context(context):
    # Fetch user products
    user_products = get_user_products()
    
    # Add user products to the context
    context.user_products = user_products

    return context
