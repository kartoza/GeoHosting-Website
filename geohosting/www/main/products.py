import frappe


def get_context(context):
    # Fetch stock items from database
    stock_items = frappe.get_all("Item", 
                                 filters={"is_stock_item": 1, 
                                          "disabled": 0, 
                                          "item_group": "GeoHosting",
                                          "variant_of": ""},  # Filter out variants
                                 fields=["name", "item_name", "item_group", "stock_uom", "description", "disabled", "image"])

    # Add filtered stock items to the context
    context.stock_items = stock_items

    return context


