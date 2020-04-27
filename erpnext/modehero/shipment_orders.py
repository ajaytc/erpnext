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

   
  
    
