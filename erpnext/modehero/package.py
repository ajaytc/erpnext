import frappe
import json
from frappe.email.doctype.notification.notification import sendCustomEmail

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
        createShipmentOrderForPackage(data)
    packOrder.save()

    return packOrder

def createShipmentOrderForPackage(data):
    
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    shipmentOrder=frappe.get_doc({
        'doctype': 'Shipment Order',
        'tracking_number':data['tracking_number'],
        'carrier_company':data['carrier'],
        'shipping_date':data['shipment_date'],
        'expected_delivery_date':data['expected_date'],
        'shipping_price':data['shipping_price'],
        'html_tracking_link':data['html_tracking_link'],
        'packaging_order_id':data['order'],
        'brand':brand
    })
    shipmentOrder.insert()
    frappe.db.commit()

@frappe.whitelist()
def submit_payment_proof(data):
    data = json.loads(data)
    packOrder = frappe.get_doc('Packaging Order', data['order'])
    packOrder.payment_proof = data['payment_proof']
    packOrder.comment = data['comment']
    packOrder.confirmation_reminder=data['confirmation_reminder']
    packOrder.profoma_reminder=data['proforma_reminder']
    packOrder.payment_reminder=data['payment_reminder']
    packOrder.shipment_reminder=data['shipment_reminder']
    packOrder.reception_reminder=data['reception_reminder']
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
        'destination': data['production_factory'],
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
    sendNotificationEmail(order)
    return {'status': 'ok', 'order': order}

def sendNotificationEmail(order):
    notification=frappe.get_doc("Notification","Order Recieved")
    vendor=frappe.get_doc("Supplier",order.packaging_vendor)
    templateData={}
    templateData['SNF']=vendor.supplier_name
    templateData['order_name']=order.name
    templateData['brand']=order.brand
    templateData['order_type']='packaging'
    templateData['recipient']=vendor.email
    templateData['country']=vendor.country
    templateData['notification']=notification

    if(vendor.email != None):
        sendCustomEmail(templateData)

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


@frappe.whitelist()
def get_item(vendor):
    return frappe.get_all('Packaging Item', filters={'packaging_vendor': vendor}, fields=['name', 'internal_ref'])
