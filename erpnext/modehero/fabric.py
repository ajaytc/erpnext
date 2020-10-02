import frappe
import json
from frappe.email.doctype.notification.notification import sendCustomEmail


@frappe.whitelist(allow_email_guest=True)
def submit_fabric_vendor_summary_info(data):
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

    fabricOrder = frappe.get_doc('Fabric Order', data['order'])

    if(("Fabric Vendor" in roles) or (frappe.session.user == 'Guest')):
        if(fabricOrder.docstatus!=2):
            checkNSendDocSubmitMail(fabricOrder,data)

    fabricOrder.ex_work_date = data['ex_work_date']
    fabricOrder.confirmation_doc = conf_doc
    fabricOrder.profoma = profoma
    fabricOrder.invoice = invoice
    fabricOrder.carrier = data['carrier']
    fabricOrder.tracking_number = data['tracking_number']
    fabricOrder.shipment_date = data['shipment_date']
    fabricOrder.production_comment = data['production_comment']
    hasShipment=(fabricOrder.docstatus==3)
    if(fabricOrder.docstatus!=2):
        fabricOrder.docstatus=0
        if(fabricOrder.confirmation_doc != None or fabricOrder.profoma != None):
            fabricOrder.docstatus = 1
        if(fabricOrder.invoice != None):
            fabricOrder.docstatus = 4
        if(fabricOrder.carrier!='' or fabricOrder.tracking_number!='' or fabricOrder.shipment_date!=''):
            fabricOrder.docstatus = 3
            createShipmentOrderForFabric(data)
        elif hasShipment:
            frappe.db.delete("Shipment Order",{'fabric_order_id': fabricOrder.name})

    try:
        fabricOrder.save()
        return fabricOrder
    except:
        frappe.throw(frappe._("Canceled Orders can't modify"))
    

    

def checkNSendDocSubmitMail(fabricOrder,data):
    document_type=''
    if(fabricOrder.confirmation_doc == None and data['confirmation_doc']!='None'):
        document_type='confirmation document'
        sendDocSubmitMail(fabricOrder,document_type)
        
    if(fabricOrder.profoma == None and data['profoma']!='None'):
        document_type='profoma'
        sendDocSubmitMail(fabricOrder,document_type)
        
    if(fabricOrder.invoice == None and data['invoice']!='None'):
        document_type='invoice'
        sendDocSubmitMail(fabricOrder,document_type)
    
    


def sendDocSubmitMail(fabricOrder,document_type):

    notification=frappe.get_doc("Notification","Document added to an order summary")
    vendor=frappe.get_doc("Supplier",fabricOrder.fabric_vendor)
    recipient=frappe.get_doc('User',fabricOrder.owner) 

    templateData={}
    templateData['SNF']=vendor.supplier_name
    templateData['internal_ref']=fabricOrder.internal_ref
    templateData['brand']=fabricOrder.brand
    templateData['order_date']=fabricOrder.creation.date()
    templateData['order_type']='fabric'
    templateData['order_name']=fabricOrder.name
    templateData['document_type']=document_type
    templateData['recipient']=recipient.email
    templateData['lang']=recipient.language
    templateData['notification']=notification

    if(recipient.email != None):
        sendCustomEmail(templateData)

def createShipmentOrderForFabric(data):
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name

    shipmentOrderName=frappe.get_all('Shipment Order', fields=['name'], filters={'fabric_order_id': data['order']})
    
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
            'fabric_order_id':data['order'],
            'brand':brand
        })
        shipmentOrder.insert()
        frappe.db.commit()


@frappe.whitelist(allow_email_guest=True)
def submit_payment_proof(data):
    data = json.loads(data)
    fabricOrder = frappe.get_doc('Fabric Order', data['order'])
    fabricOrder.payment_proof = data['payment_proof']
    fabricOrder.comment = data['comment']
    fabricOrder.confirmation_reminder = data['confirmation_reminder']
    fabricOrder.profoma_reminder = data['proforma_reminder']
    fabricOrder.payment_reminder = data['payment_reminder']
    fabricOrder.shipment_reminder = data['shipment_reminder']
    fabricOrder.reception_reminder = data['reception_reminder']
    fabricOrder.save()
    frappe.db.commit()

    return fabricOrder


@frappe.whitelist()
def create_fabric_order(data):
    if not(isinstance(data, dict)):
        data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    order_data_obj = {
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
    }
    if (order_data_obj["product_name"]==None and "item_list" in data):
        order_data_obj["product_list"] = data["item_list"]
    order = frappe.get_doc(order_data_obj)
    order.insert()
    frappe.db.commit()
    sendFabricOrderNotificationEmail(order)
    return {'status': 'ok', 'order': order}


def sendFabricOrderNotificationEmail(order):
    notification = frappe.get_doc("Notification", "Order Recieved")
    vendor = frappe.get_doc("Supplier", order.fabric_vendor)
    templateData = {}
    templateData['SNF'] = vendor.supplier_name
    templateData['order_name'] = order.name
    templateData['brand'] = order.brand
    templateData['order_type'] = 'fabric'
    templateData['recipient'] = vendor.email
    templateData['country'] = vendor.country
    templateData['notification'] = notification

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
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    return frappe.get_all('Fabric', filters={'fabric_vendor': vendor,'brand':brand}, fields=['name', 'fabric_ref'])

@frappe.whitelist()
def get_fabric_price(fabric_ref):
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    try:
        price= frappe.get_all('Fabric', filters={'fabric_ref': fabric_ref,'brand':brand}, fields=['name', 'price'])
        return price[0]
    except:
        return None

@frappe.whitelist()
def get_fabric_color():
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    try:
        colors= frappe.get_list('Color',fields=['name', 'color_name'])
        result = []
        for x in colors:
            result.append({
                'label': x.color_name,
                'value': x.color_name
            })
        return result
    except:
        return None
    
@frappe.whitelist()
def get_fabric_composition():
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    try:
        compositions= frappe.get_list('Composition',fields=['name', 'composition_name'])
        result = []
        for x in compositions:
            result.append({
                'label': x.composition_name,
                'value': x.composition_name
            })
        return result
    except:
        return None

@frappe.whitelist()
def get_fabric_width():
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    try:
        width= frappe.get_list('Width',fields=['name', 'width'])
        result = []
        for x in width:
            result.append({
                'label': x.width,
                'value': x.width
            })
        return result
    except:
        return None

def test1(doc,method):
    k=doc.owner

    


@frappe.whitelist(allow_email_guest=True)
def deleteDoc(data):
    data = json.loads(data)
    order_name = data['order']
    doc = data['doc_type']
    order = frappe.get_doc("Fabric Order", order_name)

    if(doc=='confirmation_doc'):
        order.confirmation_doc=None
    elif (doc=='profoma'):
        order.profoma=None
    elif (doc=='invoice'):
        order.invoice=None
    fabricOrder=changeDocStatus(order)
    fabricOrder.save()
    frappe.db.commit()
    return {'status': 'ok'}


def changeDocStatus(fabricOrder):
    fabricOrder.docstatus = 0
    if(fabricOrder.confirmation_doc != None or fabricOrder.profoma != None):
        fabricOrder.docstatus = 1
    if(fabricOrder.invoice != None):
        fabricOrder.docstatus = 4
    if(fabricOrder.carrier != '' or fabricOrder.tracking_number != '' or fabricOrder.shipment_date != None):
        fabricOrder.docstatus = 3
    return fabricOrder
