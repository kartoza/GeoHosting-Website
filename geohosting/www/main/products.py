import frappe

no_cache = 1

def get_context(context):
    stock_items = frappe.get_all("Item", 
                                 filters={
                                        # "is_stock_item": 1, 
                                          "disabled": 0, 
                                          "item_group": "GeoHosting",
                                          "variant_of": "",
                                          "has_variants": 1},
                                 fields=["name", "item_name", "item_group", "stock_uom", "description", "disabled", "image"])

    context.stock_items = stock_items

    return context