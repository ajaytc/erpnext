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
    #send email to brand
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
    brand=frappe.get_doc("Company",recipient.brand_name)

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
    templateData['dashboard_link']="/supply-dashboard?type="+orderType
    templateData['isSubscribed']=(brand.enabled==1)
    templateData['notification'] = notification
    # {{order_type}}-summary?order={{order_name}}&amp;sk=1

    # if(recipient.email != None):
    #     sendCustomEmail(templateData)


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
        suppliers = frappe.get_all('Brand Suppliers', filters={'brand': brand},fields=['parent'])
        allsupps=[]
        for sup in suppliers:
            supplier = frappe.get_doc("Supplier",sup['parent'])
            if (supplier.supplier_group==supplierType):
                allsupps.append(supplier.supplier_name)

        result = []
        for x in allsupps:
            result.append({
                'label': x,
                'value': x
            })
        return result
    except Exception as e:
        print(e)


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

def add_brand_supplier(doc,method):
    child_dic = {
                    "factory":doc.name,
                    "brand": doc.brand
                }
    doc.append("assigned_brands",child_dic)
    doc.save()
    frappe.db.commit()

@frappe.whitelist()
def get_official_suppliers(group):
    if group == "Fabric":
        query = {'is_official': 1,"supplier_group":"Fabric"}
    elif group=="Trimming":
        query = {'is_official': 1,"supplier_group":"Trimming"}
    elif group=="Packaging":
        query = {'is_official': 1,"supplier_group":"Packaging"}
    else:
        query = {'is_official': 1}
    try:
        suppliers = frappe.get_all('Supplier', filters=query, fields=['name'])
        result = []
        for x in suppliers:
            result.append({
                'label': x.name,
                'value': x.name
            })
        return result
    except:
        return []

@frappe.whitelist()
def get_official_supplier_data(supplier_name):
    official_facs = frappe.get_all("Supplier",{"name":supplier_name,"is_official":1},["name","contact","email","address1","adress2","phone","city","country","zip_code","tax_id","supplier_group"])
    if len(official_facs)==0:
        return {"status":"error"}
    return {"status":"ok","data":official_facs[0]}

@frappe.whitelist()
def get_official_supplier_list(group):
    if group == "fabric":
        query = {'is_official': 1,"supplier_group":"Fabric"}
    elif group=="trimming":
        query = {'is_official': 1,"supplier_group":"Trimming"}
    elif group=="packaging":
        query = {'is_official': 1,"supplier_group":"Packaging"}
    else:
        query = {'is_official': 1}
    try:
        suppliers = frappe.get_all('Supplier', filters=query, fields=['name'])
        result = []
        for x in suppliers:
            result.append(x.name)
        return result
    except:
        return []

def get_sups_by_brand(brand,sup_type):
    result = []
    all_sups = frappe.get_all('Brand Suppliers',{'brand':brand},['name','parent'] )
    for sup in all_sups:
        supplier = frappe.get_all("Supplier",{"name":sup["parent"],"supplier_group":sup_type},["is_official","name"])
        if len(supplier)>0:
            result.append(supplier[0])
    return result