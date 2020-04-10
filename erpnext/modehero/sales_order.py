import frappe


@frappe.whitelist()
def create_sales_order(items):
    todo = frappe.get_doc(
        {"doctype": "Sales Order",
         "name": "3",
         "internal_ref": "testing so",
         "customer": "Customer 1",
         "company": "Brand 1",
         "conversion_rate": 1,
         "plc_conversion_rate": 1,
         "items": [
             {
                 "item_name": "00001",
                 "item_code": "00001",
                 "qty": 1,
                 "rate": 5,
                 "warehouse": "",
                 "uom": "pcs",
                 "conversion_factor": 1
             }
         ],
            "price_list_currency": "USD",
         })
    todo.insert()
    frappe.db.commit()
    return {'status': 'ok'}
