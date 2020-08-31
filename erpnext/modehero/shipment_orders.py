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
    validated,message = size_quantity_validation(data["shipment_quantity_per_size"],data["internal_ref_prod_order"])
    if (not validated):
        return {"status":"error","message":message}
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    if (len(data['tracking_number'].strip())==0 or len(data['internal_ref_prod_order'].strip())==0 ):
        return {"status":"error","message":"Incompleted data !"}
    shipment_quantity_per_size_data = []
    for size in data['shipment_quantity_per_size']:
        shipment_quantity_per_size_data.append({"size":size,"quantity":int(data['shipment_quantity_per_size'][size])})
    shipmentOrder=frappe.get_doc({
        'doctype': 'Shipment Order',
        'tracking_number':data['tracking_number'],
        'carrier_company':data['carrier_company'],
        'shipping_date':data['shipping_date'],
        'expected_delivery_date':data['expected_delivery_date'],
        'shipping_price':data['shipping_price'],
        'html_tracking_link':data['html_tracking_link'],
        # internal_ref_prod_order shoul be None if that particular shipment is a another kind of shipment but product
        'internal_ref_prod_order':data['internal_ref_prod_order'],
        'shipment_quantity_per_size':shipment_quantity_per_size_data,
        'brand':brand
    })
    order = shipmentOrder.insert()
    frappe.db.commit()
    return {"status":"ok"}

def size_quantity_validation(size_qty_obj,internal_ref_prod_order):

    prod_order_list = frappe.get_all("Production Order",{"internal_ref":internal_ref_prod_order},["product_name"])
    if len(prod_order_list)==0:
        return False
    stock_doc = frappe.get_doc("Stock",frappe.get_all("Stock",{'item_type': 'product', 'product':prod_order_list[0].product_name},["name"])[0].name)
    count = 0
    is_not_enogh = False
    for size_req in size_qty_obj:
        for size_stock in stock_doc.product_stock_per_size:
            if size_req == size_stock.size:
                count = count + 1
                if int(size_qty_obj[size_req])>int(size_stock.quantity):
                    is_not_enogh = True
                    break
        if is_not_enogh==True:
            break
    
    if (count!=len(size_qty_obj.keys())):
        return False,"Error of data !"
    elif is_not_enogh:
        return False, "Stock Insufficient !"
    return True,None

