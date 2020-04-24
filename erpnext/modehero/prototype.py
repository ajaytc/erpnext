import frappe
import json
import ast


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
        'fabric_consumption': data['fabric_consumption'],
        'trimming-item': data['trimming_item'],
        'trimming_consumption': data['trimming_consumption'],
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


@frappe.whitelist()
def submit_production_info(data):
    data = json.loads(data)
    order = frappe.get_doc('Prototype Order', data['order'])
    order.ex_work_date = data['ex_work_date']
    order.invoice = data['invoice']
    order.tracking_number = data['tracking_number']
    order.carrier = data['carrier']
    order.shipment_date = data['shipment_date']
    order.shipment_price = data['shipment_price']
    order.production_comment = data['production_comment']
    order.save()
    return order


@frappe.whitelist()
def set_finish(orderslist):
    orderslist = ast.literal_eval(orderslist)
    res_status = "ok"
    for order in orderslist:
        order = frappe.get_doc('Prototype Order', order)
        if (order):
            order.docstatus = 1
            order.save()
        else:
            res_status = "no"
    frappe.db.commit()
    return {'status': res_status}
