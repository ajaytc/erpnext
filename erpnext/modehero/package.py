import frappe
import json


@frappe.whitelist()
def submit_pack_vendor_summary_info(data):
    data = json.loads(data)
    packOrder = frappe.get_doc('Packaging Order', data['order'])
    packOrder.ex_work_date = data['ex_work_date']
    packOrder.confirmation_doc = data['confirmation_doc']
    packOrder.profoma = data['profoma']
    packOrder.invoice = data['invoice']
    packOrder.carrier = data['carrier']
    packOrder.tracking_number = data['tracking_number']
    packOrder.shipment_date = data['shipment_date']
    packOrder.production_comment = data['production_comment']
    if(packOrder.confirmation_doc != 'None' or packOrder.profoma != 'None' or packOrder.invoice != 'None' or packOrder.ex_work_date):
        packOrder.docstatus = 4
    if(packOrder.carrier or packOrder.tracking_number or packOrder.shipment_date):
        packOrder.docstatus = 3
    packOrder.save()

    return packOrder


@frappe.whitelist()
def submit_payment_proof(data):
    data = json.loads(data)
    packOrder = frappe.get_doc('Packaging Order', data['order'])
    packOrder.payment_proof = data['payment_proof']
    packOrder.comment = data['comment']
    packOrder.save()
    frappe.db.commit()

    return packOrder


@frappe.whitelist()
def create_packaging_order(data):
    data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    order = frappe.get_doc({
        'doctype': 'Packaging Order',
        'brand': brand,
        'packaging_vendor': data['packaging_vendor'],
        'internal_ref': data['internal_ref'],
        'packaging_item': data['packaging_item'],
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
def create_packaging(data):
    data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    packaging = frappe.get_doc({
        'doctype': 'Packaging Item',
        'brand': brand,
        'packaging_vendor': data['vendor'],
        'color': data['color'],
        'packaging_material': data['material'],
        'other_info': data['other_info'],
        'packaging_size': data['size'],
        'vendor_ref': data['vendor_ref'],
        'internal_ref': data['internal_ref'],
    })
    packaging.insert()
    frappe.db.commit()
    return {'status': 'ok', 'item': packaging}
