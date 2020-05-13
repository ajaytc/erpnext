import frappe
import json


@frappe.whitelist()
def submit_trim_vendor_summary_info(data):
    data = json.loads(data)
    trimOrder = frappe.get_doc('Trimming Order', data['order'])
    trimOrder.ex_work_date = data['ex_work_date']
    trimOrder.confirmation_doc = data['confirmation_doc']
    trimOrder.profoma = data['profoma']
    trimOrder.invoice = data['invoice']
    trimOrder.carrier = data['carrier']
    trimOrder.tracking_number = data['tracking_number']
    trimOrder.shipment_date = data['shipment_date']
    trimOrder.production_comment = data['production_comment']
    if(trimOrder.confirmation_doc != 'None' or trimOrder.profoma != 'None' or trimOrder.invoice != 'None' or trimOrder.ex_work_date):
        trimOrder.docstatus = 4
    if(trimOrder.carrier or trimOrder.tracking_number or trimOrder.shipment_date):
        trimOrder.docstatus = 3

    trimOrder.save()

    return trimOrder


@frappe.whitelist()
def submit_payment_proof(data):
    data = json.loads(data)
    trimOrder = frappe.get_doc('Trimming Order', data['order'])
    trimOrder.payment_proof = data['payment_proof']
    trimOrder.comment = data['comment']
    trimOrder.save()
    frappe.db.commit()

    return trimOrder


@frappe.whitelist()
def create_trimming_order(data):
    data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    order = frappe.get_doc({
        'doctype': 'Trimming Order',
        'brand': brand,
        'trimming_vendor': data['trimming_vendor'],
        'internal_ref': data['internal_ref'],
        'trimming_item': data['trimming_item'],
        'product_name': data['item_code'],
        'production_factory': data['production_factory'],
        'quantity': int(data['quantity']),
        'in_stock': int(data['in_stock']),
        'price_per_unit': data['price_per_unit'],
        'total_price': data['total_price'],
        'profoma_reminder': data['profoma_reminder'],
        'confirmation_reminder': data['confirmation_reminder'],
        'payment_reminder': data['payment_reminder'],
        'reception_reminder': data['reception_reminder'],
        'shipment_reminder': data['shipment_reminder']
    })
    order.insert()
    frappe.db.commit()
    return {'status': 'ok', 'order': order}


@frappe.whitelist()
def create_trimming(data):
    data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    trimming = frappe.get_doc({
        'doctype': 'Trimming Item',
        'brand': brand,
        'trimming_vendor': data['vendor'],
        'item_category': data['item_category'],
        'color': data['color'],
        'material': data['material'],
        'other_info': data['other_info'],
        'trimming_size': data['size'],
        'vendor_ref': data['vendor_ref'],
        'internal_ref': data['internal_ref'],
    })
    trimming.insert()
    frappe.db.commit()
    return {'status': 'ok', 'item': trimming}


@frappe.whitelist()
def get_item(vendor):
    return frappe.get_all('Trimming Item', filters={'trimming_vendor': vendor}, fields=['name', 'internal_ref'])
