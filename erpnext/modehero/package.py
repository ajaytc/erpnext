import frappe
import json
from frappe.email.doctype.notification.notification import sendCustomEmail

@frappe.whitelist(allow_email_guest=True)
def submit_pack_vendor_summary_info(data):
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

    packOrder = frappe.get_doc('Packaging Order', data['order'])

    if("Packaging Vendor" in roles or (frappe.session.user == 'Guest')):
        if(packOrder.docstatus!=2):
            checkNSendDocSubmitMail(packOrder,data)

    packOrder.ex_work_date = data['ex_work_date']
    packOrder.confirmation_doc = conf_doc
    packOrder.profoma =profoma
    packOrder.invoice = invoice
    packOrder.carrier = data['carrier']
    packOrder.tracking_number = data['tracking_number']
    packOrder.shipment_date = data['shipment_date']
    packOrder.production_comment = data['production_comment']
    hasShipment=(packOrder.docstatus==3)
    if(packOrder.docstatus!=2):
        packOrder.docstatus=0
        if(packOrder.confirmation_doc != None or packOrder.profoma != None):
            packOrder.docstatus = 1
        if(packOrder.invoice != None):
            packOrder.docstatus = 4
        if(packOrder.carrier!='' or packOrder.tracking_number!='' or packOrder.shipment_date!=''):
            packOrder.docstatus = 3
            createShipmentOrderForPackage(data)
        elif hasShipment:
            frappe.db.delete("Shipment Order",{'packaging_order_id': packOrder.name})
    try:
        packOrder.save()
        return packOrder
    except:
        frappe.throw(frappe._("Canceled Orders can't modify"))
    

    

def checkNSendDocSubmitMail(packOrder,data):
    document_type=''
    if(packOrder.confirmation_doc == None and data['confirmation_doc']!='None'):
        document_type='confirmation document'
        sendDocSubmitMail(packOrder,document_type)
        
    if(packOrder.profoma == None and data['profoma']!='None'):
        document_type='profoma'
        sendDocSubmitMail(packOrder,document_type)
        
    if(packOrder.invoice == None and data['invoice']!='None'):
        document_type='invoice'
        sendDocSubmitMail(packOrder,document_type)
    
    


def sendDocSubmitMail(packOrder,document_type):

    notification=frappe.get_doc("Notification","Document added to an order summary")
    vendor=frappe.get_doc("Supplier",packOrder.packaging_vendor)
    recipient=frappe.get_doc('User',packOrder.owner)

    brand=frappe.get_doc("Company",packOrder.brand)  

    templateData={}
    templateData['SNF']=vendor.supplier_name
    templateData['internal_ref']=packOrder.internal_ref
    templateData['brand']=packOrder.brand
    templateData['order_date']=packOrder.creation.date()
    templateData['order_type']='packaging'
    templateData['order_name']=packOrder.name
    templateData['document_type']=document_type
    templateData['recipient']=recipient.email
    templateData['lang']=recipient.language
    templateData['dashboard_link']="/supply-dashboard"
    templateData['isSubscribed']=(brand.enabled==1)
    templateData['notification']=notification

    if(recipient.email != None):
        sendCustomEmail(templateData)

def createShipmentOrderForPackage(data):
    
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name

    shipmentOrderName=frappe.get_all('Shipment Order', fields=['name'], filters={'packaging_order_id': data['order']})
    
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
            'packaging_order_id':data['order'],
            'brand':brand
        })
        shipmentOrder.insert()
        frappe.db.commit()

@frappe.whitelist(allow_email_guest=True)
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
    if not(isinstance(data, dict)):
        data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    order_data_obj = {
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
    }
    if (order_data_obj["product_name"]==None and "item_list" in data):
        order_data_obj["product_list"] = data["item_list"]
    order = frappe.get_doc(order_data_obj)
    order.insert()
    frappe.db.commit()
    sendPackagingOrderNotificationEmail(order)
    return {'status': 'ok', 'order': order}

def sendPackagingOrderNotificationEmail(order):
    notification=frappe.get_doc("Notification","Order Recieved")
    vendor=frappe.get_doc("Supplier",order.packaging_vendor)
    templateData={}
    templateData['SNF']=vendor.supplier_name
    templateData['order_name']=order.name
    templateData['brand']=order.brand
    templateData['order_type']='packaging'
    templateData['recipient']=vendor.email
    templateData['country']=vendor.country
    templateData['dashboard_link']="/supply-dashboard"
    templateData['isSubscribed']=(vendor.is_official==1)
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
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    return frappe.get_all('Packaging Item', filters={'packaging_vendor': vendor,'brand':brand}, fields=['name', 'internal_ref'])

@frappe.whitelist()
def get_packaging_material():
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    try:
        material= frappe.get_list('Packaging Material',fields=['name', 'material_name'])
        result = []
        for x in material:
            result.append({
                'label': x.material_name,
                'value': x.name
            })
        return result
    except:
        return None
    
@frappe.whitelist()
def get_packaging_size():
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    try:
        size= frappe.get_list('Packaging Size',fields=['name', 'size_name'])
        result = []
        for x in size:
            result.append({
                'label': x.size_name,
                'value': x.name
            })
        return result
    except:
        return None
    





@frappe.whitelist(allow_email_guest=True)
def deleteDoc(data):
    data = json.loads(data)
    order_name = data['order']
    doc = data['doc_type']
    order = frappe.get_doc("Packaging Order", order_name)

    if(doc=='confirmation_doc'):
        order.confirmation_doc=None
    elif (doc=='profoma'):
        order.profoma=None
    elif (doc=='invoice'):
        order.invoice=None
    packOrder=changeDocStatus(order)
    packOrder.save()
    frappe.db.commit()
    return {'status': 'ok'}


def changeDocStatus(packOrder):
    packOrder.docstatus = 0
    if(packOrder.confirmation_doc != None or packOrder.profoma != None):
        packOrder.docstatus = 1
    if(packOrder.invoice != None):
        packOrder.docstatus = 4
    if(packOrder.carrier != '' or packOrder.tracking_number != '' or packOrder.shipment_date != None):
        packOrder.docstatus = 3
    return packOrder

def set_relevent_attributes_for_packaging_save(doc,method):
    brand=doc.brand
    materials=frappe.get_all("Packaging Material",filters={"brand":brand,"material_name":doc.packaging_material})
    colors=frappe.get_all("Color",filters={"brand":brand,"color_name":doc.color})
    sizes=frappe.get_all("Packaging Size",filters={"brand":brand,"size_name":doc.packaging_size})
    if(len(materials)>0):
        doc.packaging_material=materials[0].name
    if(len(colors)>0):
        doc.color=colors[0].name
    if(len(sizes)>0):
        doc.packaging_size=sizes[0].name
    
    return doc

@frappe.whitelist()
def get_size_name(size):
    size = frappe.get_doc('Packaging Size',size).size_name
    return size

@frappe.whitelist()
def get_material_name(material):
    material = frappe.get_doc('Packaging Material',material).material_name
    return material