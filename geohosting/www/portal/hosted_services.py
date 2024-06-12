import frappe

no_cache = 1
def get_user_products():
    try:
        user = frappe.session.user
        
        user_products = frappe.get_all("User Products", filters={"user": user}, fields=["name", "product", "specifications", "status", "product_meta", "logo"])
        
        return user_products
    except Exception as e:
        frappe.log_error(f"Failed to fetch user products for {user}: {str(e)}")
        return []

def get_context(context):
    try:
        user_products = get_user_products()
        
        context.user_products = user_products

    except Exception as e:
        frappe.log_error(f"Failed to fetch user products: {str(e)}")
        context.user_products = []

    return context

