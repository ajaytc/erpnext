import frappe
import json


@frappe.whitelist()
def create_production_order(data):
    data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    order = frappe.get_doc({
        'doctype': 'Production Order',
        'product_category': data['product_category'],
        'internal_ref': data['internal_ref'],
        'product_name': data['product_name'],
        'fabric_ref': data['fabric_ref'],
        'trimming': data['trimming_item'],
        'packaging': data['packaging_item'],
        'production_factory': data['production_factory'],
        'quantity_per_size': data['quantity'],
        'comment': data['comment'],
        'brand': brand
    })

    order.insert()
    return {'status': 'ok', 'order': order}
