import frappe
import json


@frappe.whitelist()
def submit_fabric_vendor_summary_info(data):
    data = json.loads(data)
    fabricOrder = frappe.get_doc('Fabric Order', data['order'])
    fabricOrder.ex_work_date = data['ex_work_date']
    fabricOrder.confirmation_doc = data['confirmation_doc']
    fabricOrder.profoma = data['profoma']
    fabricOrder.invoice = data['invoice']
    fabricOrder.carrier = data['carrier']
    fabricOrder.tracking_number = data['tracking_number']
    fabricOrder.shipment_date = data['shipment_date']
    fabricOrder.production_comment = data['production_comment']
    if(fabricOrder.confirmation_doc != 'None' or fabricOrder.profoma != 'None' or fabricOrder.invoice != 'None' or fabricOrder.ex_work_date):
        fabricOrder.docstatus = 4
    if(fabricOrder.carrier or fabricOrder.tracking_number or fabricOrder.shipment_date):
        fabricOrder.docstatus = 3

    fabricOrder.save()

    return fabricOrder


@frappe.whitelist()
def submit_payment_proof(data):
    data = json.loads(data)
    fabricOrder = frappe.get_doc('Fabric Order', data['order'])
    fabricOrder.payment_proof = data['payment_proof']
    fabricOrder.comment = data['comment']
    fabricOrder.save()
    frappe.db.commit()

    return fabricOrder

@frappe.whitelist()
def create_fabric_order(data):
    data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    order = frappe.get_doc({
        'doctype': 'Fabric Order',
        'brand' : brand,
        'fabric_vendor' : data['fabric_vendor'],
        'internal_ref' : data['internal_ref'],
        'fabric_ref' : data['fabric_ref'],
        'product_name' : data['item_code'],
        'production_factory' : data['production_factory'],
        'quantity' : int(data['quantity']),
        'in_stock' : int(data['in_stock']),
        'price_per_unit' : data['price_per_unit'],
        'total_price' : data['total_price'],
        'profoma_reminder' : data['profoma_reminder'],
        'confirmation_reminder' : data['confirmation_reminder'],
        'payment_reminder' : data['payment_reminder'],
        'reception_reminder' : data['reception_reminder'],
        'shipment_reminder' : data['shipment_reminder']
    })
    order.insert()
    frappe.db.commit()
    return {'status': 'ok', 'order': order}