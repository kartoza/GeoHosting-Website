import frappe

# def get_context(context):

#     products = frappe.db.sql("""SELECT product_name, product_description, product_price, product_image FROM `tabProducts`;""", as_dict=True)
#     context.products = products

#     return context

def get_context(context):
    # Fetch stock items from ERPNext database
    stock_items = frappe.get_all("Item", 
                                 filters={"is_stock_item": 1, "disabled": 0, "item_group": "GeoHosting"}, 
                                 fields=["name", "item_name", "item_group", "stock_uom", "description", "disabled", "image"])

    # Add filtered stock items to the context
    context.stock_items = stock_items

    return context




@frappe.whitelist(allow_guest=True)
def get_product_details(product_id=None):
    # Fetch product details based on the provided product ID
    product = frappe.get_doc("Products", product_id)

    if product:
        return {
            "name": product.item_name,
            "description": product.description,
            "image": product.image
        }
    else:
        return {"error": "Product not found"}