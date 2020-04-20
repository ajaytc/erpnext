import frappe
import json


@frappe.whitelist()
def create_prototype_order(data):
    data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
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
        'comment': data['comment'],
        'brand': brand
    })

    order.insert()
    return {'status': 'ok', 'order': order}


@frappe.whitelist()
def validate(order, isvalidate):
    order = frappe.get_doc('Prototype Order', order)
    if isvalidate == 'true':
        order.docstatus = 1
    else:
        order.docstatus = 1
        order.save()
        order.docstatus = 2
    order.save()
    frappe.db.commit()
    return order
