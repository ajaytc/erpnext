import frappe
import json
from frappe.email.doctype.notification.notification import sendCustomEmail


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
        createShipmentOrderForFabric(data)

    fabricOrder.save()

    return fabricOrder


def createShipmentOrderForFabric(data):
    
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
        'fabric_order_id':data['order'],
        'brand':brand
    })
    shipmentOrder.insert()
    frappe.db.commit()

@frappe.whitelist()
def submit_payment_proof(data):
    data = json.loads(data)
    fabricOrder = frappe.get_doc('Fabric Order', data['order'])
    fabricOrder.payment_proof = data['payment_proof']
    fabricOrder.comment = data['comment']
    fabricOrder.confirmation_reminder=data['confirmation_reminder']
    fabricOrder.profoma_reminder=data['proforma_reminder']
    fabricOrder.payment_reminder=data['payment_reminder']
    fabricOrder.shipment_reminder=data['shipment_reminder']
    fabricOrder.reception_reminder=data['reception_reminder']
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
        'brand': brand,
        'fabric_vendor': data['fabric_vendor'],
        'internal_ref': data['internal_ref'],
        'fabric_ref': data['fabric_ref'],
        'product_name': data['item_code'],
        'production_factory': data['production_factory'],
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
    vendor=frappe.get_doc("Supplier",order.fabric_vendor)
    templateData={}
    templateData['SNF']=vendor.supplier_name
    templateData['order_name']=order.name
    templateData['brand']=order.brand
    templateData['order_type']='fabric'
    templateData['recipient']=vendor.email
    templateData['country']=vendor.country
    templateData['notification']=notification

    if(vendor.email != None):
        sendCustomEmail(templateData)
    



@frappe.whitelist()
def create_fabric(data):
    data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    fabric = frappe.get_doc({
        'doctype': 'Fabric',
        'brand': brand,
        'fabric_ref': data['ref'],
        'fabric_vendor': data['vendor'],
        'color': data['color'],
        'width': data['width'],
        'composition': data['composition'],
    })
    fabric.insert(ignore_permissions=True,)
    frappe.db.commit()
    return {'status': 'ok', 'item': fabric}


@frappe.whitelist()
def get_fabric(vendor):
    return frappe.get_all('Fabric', filters={'fabric_vendor': vendor}, fields=['name', 'fabric_ref'])
