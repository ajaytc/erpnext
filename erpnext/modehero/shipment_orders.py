import frappe
import json


@frappe.whitelist()
def deliverOrder(data):
    data = json.loads(data)
    orders=data['orders']

    for order in orders:
        orderOb=frappe.get_doc('Shipment Order',order)
        orderOb.docstatus=1
        orderOb.save()
    
    frappe.db.commit()

    return {'status':'OK'}

@frappe.whitelist()
def createShipmentOrder(data):
    data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    if (len(data['tracking_number'].strip())==0 and len(data['shipping_date'].strip())==0 and len(data['carrier_company'].strip())==0 ):
        return {"status":"error","message":"Incompleted data !"}
    try:
        shipCost=float(data['shipping_price'])
    except :
        return {"status":"error","message":"Invalid type Data !"}
    
    
    shipmentOrder=frappe.get_doc({
        'doctype': 'Shipment Order',
        'tracking_number':data['tracking_number'],
        'carrier_company':data['carrier_company'],
        'shipping_date':data['shipping_date'],
        'expected_delivery_date':data['expected_delivery_date'],
        'shipping_price':shipCost,
        'html_tracking_link':data['html_tracking_link'],
        'shipping_document':data['shipping_document'],
        'stock':data['stock'],
        'brand':brand
    })
    order = shipmentOrder.insert()
    frappe.db.commit()
    return {"status":"ok","name":order.name}

@frappe.whitelist()
def deleteshipment(shipmentName):
    shipmentOrder=frappe.get_doc('Shipment Order',shipmentName)
    shipmentOrder.delete()

    frappe.db.commit()

    return {"status":"ok","name":shipmentOrder.name}



# def updateShipmentSizeQuantitesIfSizePerQuantitesNotGiven(doc,method):
#     if doc.internal_ref_prod_order==None:
#         return None
#     elif len(doc.shipment_quantity_per_size)>0:
#         return None
#     child_doc_list = []
#     sizes_qtys = frappe.get_doc("Production Order",doc.internal_ref_prod_order).quantity_per_size
#     for size_qty in frappe.get_doc("Production Order",doc.internal_ref_prod_order).quantity_per_size:
#         child_doc = frappe.get_doc({
#             "doctype": "Shipment Quantity Per Size",
#             "parent":doc.name,
#             "parentfield": "shipment_quantity_per_size",
#             "parenttype": "Shipment Order",
#             "quantity": size_qty.quantity,
#             "size": size_qty.size,
#         })
#         child_doc.insert()
#         child_doc_list.append(child_doc)
#     frappe.db.commit()
#     doc.shipment_quantity_per_size = child_doc_list
#     doc.save()
#     frappe.db.commit()