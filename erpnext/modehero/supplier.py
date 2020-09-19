import frappe
import json
import ast
from frappe.email.doctype.notification.notification import sendCustomEmail


@frappe.whitelist()
def create_supplier(data):
    data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    supplier = frappe.get_doc({
        'doctype': 'Supplier',
        'brand': brand,
        'email': data['email'],
        'supplier_group': data['supplier_group'],
        'address1': data['address1'],
        'address2': data['address2'],
        'contact': data['contact'],
        'phone_number': data['phone_number'],
        'city': data['city'],
        'zip_code': data['zip_code'],
        'supplier_name': data['supplier_name'],
        'country': data['country']
    })
    supplier.insert()
    frappe.db.commit()
    return {'status': 'ok', 'supplier': supplier}


@frappe.whitelist()
def cancelSupplyOrder(data):
    data = json.loads(data)
    canceledOrders = data['orders']
    orderGroup = data['orderGroup']

    for order in canceledOrders:
        frappe.db.set_value(orderGroup, order, 'docstatus', 2)
        order = frappe.get_doc(orderGroup, order)
        sendNotificationEmail(order, orderGroup)

    frappe.db.commit()

    return {'status': 'ok'}


def sendNotificationEmail(order, orderGroup):
    notification = frappe.get_doc(
        "Notification", "Supply/Purchase Order Cancel/Modify")

    if(orderGroup == 'Fabric Order'):
        orderType = 'fabric'
        vendor = frappe.get_doc("Supplier", order.fabric_vendor)
    elif (orderGroup == 'Trimming Order'):
        orderType = 'trimming'
        vendor = frappe.get_doc("Supplier", order.trimming_vendor)
    else:
        orderType = 'packaging'
        vendor = frappe.get_doc("Supplier", order.packaging_vendor)

    recipient = frappe.get_doc('User', order.owner)

    templateData = {}
    templateData['recipient_name'] = order.brand
    templateData['SNF'] = vendor.supplier_name
    templateData['trigger'] = 'cancelled'
    templateData['internal_ref'] = order.internal_ref
    templateData['brand'] = order.brand
    templateData['order_date'] = order.creation.date()
    # templateData['order_type']=orderType
    templateData['order_link'] = orderType + \
        '-summary?order='+order.name+'&amp;sk=1'
    # templateData['order_name']=order.name
    templateData['recipient'] = recipient.email
    templateData['lang'] = recipient.language
    templateData['notification'] = notification
    # {{order_type}}-summary?order={{order_name}}&amp;sk=1

    if(recipient.email != None):
        sendCustomEmail(templateData)


@frappe.whitelist()
def get_supplier(suppier_ref):
    try:
        return frappe.get_doc("Supplier", suppier_ref)
    except:
        return None


@frappe.whitelist()
def get_type_wise_suppliers(supplierType):
    try:
        brand = frappe.get_doc('User', frappe.session.user).brand_name
        suppliers = frappe.get_all('Supplier', filters={'brand': brand,'supplier_group':supplierType}, fields=['name'])
        result = []
        for x in suppliers:
            result.append({
                'label': x.name,
                'value': x.name
            })
        return result
    except:
        return None


@frappe.whitelist()
def get_supply_doc(supply_ref, supply_type):
    try:
        if supply_type == "fabric":
            return frappe.get_doc("Fabric", supply_ref)
        elif supply_type == "trimming":
            return frappe.get_doc("Trimming Item", supply_ref)
        elif supply_type == "packaging":
            return frappe.get_doc("Packaging Item", supply_ref)
        else:
            return None
    except:
        return None
