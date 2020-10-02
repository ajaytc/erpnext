import frappe
import json
from frappe.email.doctype.notification.notification import sendCustomEmail


@frappe.whitelist(allow_email_guest=True)
def submit_trim_vendor_summary_info(data):
    data = json.loads(data)

    roles=frappe.get_roles(frappe.session.user)
    if(data['profoma'] == 'None'):
        profoma = None
    else:
        profoma = data['profoma']
    if (data['invoice'] == 'None'):
        invoice = None
    else:
        invoice = data['invoice']
    if(data['confirmation_doc'] == 'None'):
        conf_doc = None
    else:
        conf_doc = data['confirmation_doc']

    trimOrder = frappe.get_doc('Trimming Order', data['order'])

    if("Trimming Vendor" in roles or (frappe.session.user == 'Guest')):
        if(trimOrder.docstatus!=2):
            checkNSendDocSubmitMail(trimOrder,data)

    trimOrder.ex_work_date = data['ex_work_date']
    trimOrder.confirmation_doc = conf_doc
    trimOrder.profoma = profoma
    trimOrder.invoice = invoice
    trimOrder.carrier = data['carrier']
    trimOrder.tracking_number = data['tracking_number']
    trimOrder.shipment_date = data['shipment_date']
    trimOrder.production_comment = data['production_comment']
    hasShipment=(trimOrder.docstatus==3)
    if(trimOrder.docstatus!=2):
        trimOrder.docstatus=0
        if(trimOrder.confirmation_doc != None or trimOrder.profoma != None):
            trimOrder.docstatus = 1
        if(trimOrder.invoice != None):
            trimOrder.docstatus = 4
        if(trimOrder.carrier!='' or trimOrder.tracking_number!='' or trimOrder.shipment_date!=''):
            trimOrder.docstatus = 3
            createShipmentOrderForTrimming(data)
        elif hasShipment:
            frappe.db.delete("Shipment Order",{'trimming_order_id': trimOrder.name})


    try:
        trimOrder.save()
        return trimOrder
    except:
        return trimOrder
    


    

def checkNSendDocSubmitMail(trimOrder,data):
    document_type=''
    if(trimOrder.confirmation_doc == None and data['confirmation_doc']!='None'):
        document_type='confirmation document'
        sendDocSubmitMail(trimOrder,document_type)
        
    if(trimOrder.profoma == None and data['profoma']!='None'):
        document_type='profoma'
        sendDocSubmitMail(trimOrder,document_type)
        
    if(trimOrder.invoice == None and data['invoice']!='None'):
        document_type='invoice'
        sendDocSubmitMail(trimOrder,document_type)
    
    

def sendDocSubmitMail(trimOrder,document_type):
    
    notification=frappe.get_doc("Notification","Document added to an order summary")
    vendor=frappe.get_doc("Supplier",trimOrder.trimming_vendor)
    recipient=frappe.get_doc('User',trimOrder.owner) 

    templateData={}
    templateData['SNF']=vendor.supplier_name
    templateData['internal_ref']=trimOrder.internal_ref
    templateData['brand']=trimOrder.brand
    templateData['order_date']=trimOrder.creation.date()
    templateData['order_type']='trimming'
    templateData['order_name']=trimOrder.name
    templateData['document_type']=document_type
    templateData['recipient']=recipient.email
    templateData['lang']=recipient.language
    templateData['notification']=notification

    if(recipient.email != None):
        sendCustomEmail(templateData)

def createShipmentOrderForTrimming(data):
    
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name

    shipmentOrderName=frappe.get_all('Shipment Order', fields=['name'], filters={'trimming_order_id': data['order']})
    
    if(len(shipmentOrderName)>0):
        shipmentOrder=frappe.get_doc('Shipment Order',shipmentOrderName[0].name)
        shipmentOrder.carrier_company=data['carrier']
        shipmentOrder.tracking_number=data['tracking_number']
        shipmentOrder.shipping_date=data['shipment_date']
        shipmentOrder.expected_delivery_date=data['expected_date']
        shipmentOrder.shipping_price=data['shipping_price']
        shipmentOrder.html_tracking_link=data['html_tracking_link']

        shipmentOrder.save()
        frappe.db.commit()

    else:
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

@frappe.whitelist(allow_email_guest=True)
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
    if not(isinstance(data, dict)):
        data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    order_data_obj = {
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
    }
    if (order_data_obj["product_name"]==None and "item_list" in data):
        order_data_obj["product_list"] = data["item_list"]
    order = frappe.get_doc(order_data_obj)
    order.insert()
    frappe.db.commit()
    sendTrimmingOrderNotificationEmail(order)
    return {'status': 'ok', 'order': order}

def sendTrimmingOrderNotificationEmail(order):
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



@frappe.whitelist(allow_email_guest=True)
def deleteDoc(data):
    data = json.loads(data)
    order_name = data['order']
    doc = data['doc_type']
    order = frappe.get_doc("Trimming Order", order_name)

    if(doc=='confirmation_doc'):
        order.confirmation_doc=None
    elif (doc=='profoma'):
        order.profoma=None
    elif (doc=='invoice'):
        order.invoice=None
    trimOrder=changeDocStatus(order)
    trimOrder.save()
    frappe.db.commit()
    return {'status': 'ok'}


def changeDocStatus(trimOrder):
    trimOrder.docstatus = 0
    if(trimOrder.confirmation_doc != None or trimOrder.profoma != None):
        trimOrder.docstatus = 1
    if(trimOrder.invoice != None):
        trimOrder.docstatus = 4
    if(trimOrder.carrier != '' or trimOrder.tracking_number != '' or trimOrder.shipment_date != None):
        trimOrder.docstatus = 3
    return trimOrder

@frappe.whitelist()
def get_trimming_category():
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    try:
        category= frappe.get_list('Trimming Category',fields=['name', 'category_name'])
        result = []
        for x in category:
            result.append({
                'label': x.category_name,
                'value': x.name
            })
        return result
    except:
        return None
    