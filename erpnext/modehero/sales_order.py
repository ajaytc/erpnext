import frappe
import json


@frappe.whitelist()
def create_sales_order(items, garmentlabel, internalref):
    prepared = []
    items = json.loads(items)
    for i in items:
        prepared.append({
            "item_name": items[i]['item'],
            "item_code": items[i]['item'],
            "qty": 1,
            "rate": 1,
            "warehouse": "",
            "uom": "pcs",
            "conversion_factor": 1,
            "item_destination": items[i]['destination']
        })

    order = frappe.get_doc(
        {"doctype": "Sales Order",
         #  "name": "3",
         "internal_ref": internalref,
         "customer": "Customer 1",
         "company": "Brand 1",
         "conversion_rate": 1,
         "plc_conversion_rate": 1,
         "garment_label": garmentlabel,
         "items": prepared,
            "price_list_currency": "USD",
         })

    order.insert()

    for i in order.items:
        quantities = items[i.item_name]['quantities']
        for s in quantities:
            qty = quantities[s]

            # qtypersize = frappe.new_doc('Quantity Per Size')
            qtypersize = frappe.get_doc({
                "doctype": "Quantity Per Size",
                "size": s,
                "quantity": qty,
                "order_id": i.name
            })
            # qtypersize.size = s
            # qtypersize.quantity = qty
            # qtypersize.order_id = i.name
            qtypersize.insert()

    frappe.db.commit()

    return {'status': 'ok', 'order': order}
