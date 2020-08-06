import frappe
import json
from frappe.email.doctype.notification.notification import sendCustomEmail


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
        createShipmentOrderForTrimming(data)

    trimOrder.save()

    return trimOrder

def createShipmentOrderForTrimming(data):
    
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
        'trimming_order_id':data['order'],
        'brand':brand
    })
    shipmentOrder.insert()
    frappe.db.commit()

@frappe.whitelist()
def submit_payment_proof(data):
    data = json.loads(data)
    trimOrder = frappe.get_doc('Trimming Order', data['order'])
    trimOrder.payment_proof = data['payment_proof']
    trimOrder.comment = data['comment']
    trimOrder.confirmation_reminder=data['confirmation_reminder']
    trimOrder.profoma_reminder=data['proforma_reminder']
    trimOrder.payment_reminder=data['payment_reminder']
    trimOrder.shipment_reminder=data['shipment_reminder']
    trimOrder.reception_reminder=data['reception_reminder']
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
    vendor=frappe.get_doc("Supplier",order.trimming_vendor)
    templateData={}
    templateData['SNF']=vendor.supplier_name
    templateData['order_name']=order.name
    templateData['brand']=order.brand
    templateData['order_type']='trimming'
    templateData['recipient']=vendor.email
    templateData['country']=vendor.country
    templateData['notification']=notification

    if(vendor.email != None):
        sendCustomEmail(templateData)


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
