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

def updateShipmentSizeQuantitesIfSizePerQuantitesNotGiven(doc,method):
    if doc.internal_ref_prod_order==None:
        return None
    elif len(doc.shipment_quantity_per_size)>0:
        return None
    child_doc_list = []
    sizes_qtys = frappe.get_doc("Production Order",doc.internal_ref_prod_order).quantity_per_size
    for size_qty in frappe.get_doc("Production Order",doc.internal_ref_prod_order).quantity_per_size:
        child_doc = frappe.get_doc({
            "doctype": "Shipment Quantity Per Size",
            "parent":doc.name,
            "parentfield": "shipment_quantity_per_size",
            "parenttype": "Shipment Order",
            "quantity": size_qty.quantity,
            "size": size_qty.size,
        })
        child_doc.insert()
        child_doc_list.append(child_doc)
    frappe.db.commit()
    doc.shipment_quantity_per_size = child_doc_list
    doc.save()
    frappe.db.commit()