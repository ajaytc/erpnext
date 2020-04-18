import frappe
import json


@frappe.whitelist()
def create_prototype_order(data):
    data = json.loads(data)
    order = frappe.get_doc({
        'doctype': 'Prototype Order',
        'internal_ref': data['internal_ref'],
        'product_category': data['product_category'],
        'product': data['product'],
        'fabric_ref': data['fabric_ref'],
        'consumption': data['consumption'],
        'trimming-item': data['trimming_item'],
        'production_factory': data['production_factory'],
        'final_destination': data['destination'],
        'techpack': data['techpack'],
        'pattern': data['pattern'],
        'picture': data['picture'],
        'price_per_unit': data['price'],
        'quantity_per_size': data['quantity'],
        'comment': data['comment']
    })

    order.insert()
    return {'status': 'ok', 'order': order}
