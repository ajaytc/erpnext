import frappe
import json
import ast


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
        'fabric_consumption': data['fabric_consumption'],
        'trimming': data['trimming_item'],
        'trimming_consumption': data['trimming_consumption'],
        'packaging': data['packaging_item'],
        'packaging_consumption': data['packaging_consumption'],
        'production_factory': data['production_factory'],
        'quantity_per_size': data['quantity'],
        'comment': data['comment'],
        'brand': brand
    })

    order.insert()
    return {'status': 'ok', 'order': order}


@frappe.whitelist()
def validate(order, isvalidate):
    order = frappe.get_doc('Production Order', order)
    if isvalidate == 'true':
        order.docstatus = 1
    else:
        order.docstatus = 1
        order.save()
        order.docstatus = 2
    order.save()
    frappe.db.commit()
    return order


@frappe.whitelist()
def set_finish(orderslist):
    orderslist = ast.literal_eval(orderslist)
    res_status = "ok"
    for order in orderslist:
        order = frappe.get_doc('Production Order', order)
        if (order):
            order.docstatus = 1
            order.save()
        else:
            res_status = "no"
    frappe.db.commit()
    return {'status': res_status}


@frappe.whitelist()
def submit_production_summary_info(data):
    data = json.loads(data)
    order = frappe.get_doc('Production Order', data['order'])
    order.expected_work_date = data['ex_work_date']
    order.confirmation_doc = data['confirmation_doc']
    order.profoma = data['profoma']
    order.invoice = data['invoice']
    order.carrier = data['carrier']
    order.tracking_number = data['tracking_number']
    order.shipment_date = data['shipment_date']
    order.production_comment = data['production_comment']
    order.save()
    return order
