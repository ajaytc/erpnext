import frappe
import json


@frappe.whitelist()
def create_sales_order(items):
    prepared = []
    items = json.loads(items)
    for i in items:
        prepared.append({
            "item_name": i['item'],
            "item_code": i['item'],
            "qty": 1,
            "rate": 1,
            "warehouse": "",
            "uom": "pcs",
            "conversion_factor": 1,
            "item_destination": i['destination']
        })

    order = frappe.get_doc(
        {"doctype": "Sales Order",
         #  "name": "3",
         "internal_ref": "testing so",
         "customer": "Customer 1",
         "company": "Brand 1",
         "conversion_rate": 1,
         "plc_conversion_rate": 1,
         "items": prepared,
            "price_list_currency": "USD",
         })
    order.insert()
    frappe.db.commit()
    return {'status': 'ok', 'order': order}
