import frappe
import json
import ast
import random
from erpnext.modehero.production import create_production_order


@frappe.whitelist()
def create_sales_order(items, garmentlabel, internalref, profoma):
    prepared = []
    items = json.loads(items)
    for i in items:
        prepared.append({
            "item_name": items[i]['item'],
            "item_code": items[i]['item'],
            "qty": 1,
            "rate": 1,
            "warehouse": "",
            "uom": "pcs",
            "conversion_factor": 1,
            "item_destination": items[i]['destination']
        })

    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    customer = frappe.get_list(
        'Customer', filters={'user': frappe.session.user})
    if(len(customer) > 0):
        customer = customer[0]['name']

    order = frappe.get_doc(
        {"doctype": "Sales Order",
         "internal_ref": internalref,
         "customer": customer,
         "company": brand,
         "conversion_rate": 1,
         "plc_conversion_rate": 1,
         "garment_label": garmentlabel,
         "profoma": profoma,
         "items": prepared,
         "price_list_currency": "USD",
         })

    order.insert(ignore_permissions=True)

    for i in order.items:
        quantities = items[i.item_name]['quantities']
        for s in quantities:
            qty = quantities[s]

            # qtypersize = frappe.new_doc('Quantity Per Size')
            if qty != '':
                qtypersize = frappe.get_doc({
                    "doctype": "Quantity Per Size",
                    "size": s,
                    "quantity": qty,
                    "order_id": i.name,
                    "first_quantity":qty,
                    "product_id": i.item_code,
                    "brand": brand
                })
                qtypersize.insert(ignore_permissions=True)

    frappe.db.commit()

    return {'status': 'ok', 'order': order}


def on_remove_sales_order(doc, method):
    for i in doc.items:
        docs = frappe.get_list("Quantity Per Size",
                               filters={"order_id": i.name})
        for j in docs:
            frappe.delete_doc("Quantity Per Size", j.name)

    frappe.msgprint(frappe._("Client Purchase Order ")+doc.name + " deleted")


@frappe.whitelist()
def delete(order):
    frappe.delete_doc('Sales Order', order)
    frappe.db.commit()


@frappe.whitelist()
def duplicate(order):
    doc = frappe.get_doc('Sales Order', order)
    prepared = []

    for i in doc.items:
        prepared.append({
                        "item_name": i.item_name,
                        "item_code": i.item_code,
                        "qty": i.qty,
                        "rate": i.rate,
                        "warehouse": i.warehouse,
                        "uom": i.uom,
                        "conversion_factor": i.conversion_factor,
                        "item_destination": i.item_destination
                        })

    order = frappe.get_doc(
        {"doctype": "Sales Order",
         "internal_ref": doc.internal_ref,
         "customer": doc.customer,
         "company": doc.company,
         "conversion_rate": doc.conversion_rate,
         "plc_conversion_rate": doc.plc_conversion_rate,
         "garment_label": doc.garment_label,
         "profoma": doc.profoma,
         "items": prepared,
         "price_list_currency": doc.price_list_currency,
         })

    order.insert()

    for i in doc.items:
        qtydocs = frappe.get_list(
            'Quantity Per Size', filters={'order_id': i.name}, fields=['size', 'quantity', 'order_id'])

        for q in qtydocs:
            # get name of newly created sales order items
            order_id = next(
                item for item in order.items if item.item_name == i.item_code).name
            qtypersize = frappe.get_doc({
                "doctype": "Quantity Per Size",
                "size": q.size,
                "quantity": q.quantity,
                "order_id": order_id,
                "product_id": i.item_code,
                "brand": doc.company
            })
            qtypersize.insert()

    frappe.db.commit()
    frappe.msgprint(frappe._("Client Purchase Order ") +
                    doc.name+" duplicated as "+order.name)


@frappe.whitelist()
def cancel(order):
    order = frappe.get_doc('Sales Order', order)
    order.docstatus = 1
    order.save()
    order.docstatus = 2
    order.save()
    frappe.db.commit()
    frappe.msgprint(frappe._("Client Purchase Order ")+order.name+" cancelled")


@frappe.whitelist()
def calculate_price(products):
    # request format,
    #  products = {'0001':{'XS':1,'S':2},'0002':{'M':3}}

    # response format
    # { '0001':233123,'0002':3424324, 'total':321321313}

    prices = {}
    perpiece = {}
    products = json.loads(products)
    for p in products:
        prices[p] = 0
        for s in products[p]:
            qty = products[p][s]
            price = frappe.get_list('Prices for Quantity', filters={
                                    'parent': p, 'from': ['<=', qty], 'to': ['>=', qty]}, fields=['price'])
            if(len(price) > 0):
                prices[p] += price[0]['price']*float(qty)
                perpiece[p] = price[0]['price']

    total = 0
    for p in prices:
        total += float(prices[p])
    prices['total'] = total
    prices['perpiece'] = perpiece
    return prices


@frappe.whitelist()
def validate_order(order, products):
    products = json.loads(products)
    order = frappe.get_doc('Sales Order', order)
    order.docstatus = 1

    update_sales_order(order, products)
    order.save()
    frappe.db.commit()
    frappe.msgprint(frappe._("Client Purchase Order ")+order.name+" validated")


def update_sales_order(order, products):
    # order is sales order doc
    # products come in this dictionary format {'0001':{'XS':1,'S':2},'0002':{'M':3}}

    for i in order.items:
        qtys = frappe.get_all('Quantity Per Size',
                              filters={'order_id': i.name}, fields=['name', 'size', 'quantity'])
        for q in qtys:
            if(products[i.item_code][q['size']] != q['quantity']):
                frappe.db.set_value('Quantity Per Size', q.name, {
                    'quantity': products[i.item_code][q['size']]
                })

    frappe.db.commit()

def update_item_quantities(sales_order_item_name,item_dic):
    any_change_db = False
    item_quantites = frappe.get_all('Quantity Per Size',filters={'order_id':sales_order_item_name},fields=['name','size','quantity'])
    for size in item_dic:
        for item_quantity in item_quantites:
            if ((item_quantity['size']==size) and (item_quantity['quantity']!=item_dic[size])):
                any_change_db = True
                frappe.set_value('Quantity Per Size',item_quantity['name'],{
                    'quantity':item_dic[size]
                })
    if (any_change_db):
        frappe.db.commit()


@frappe.whitelist()
def validate_multiple_orders(orders):
    # order format = "{"a270d41181":{"L":"10","XL":"11","XXL":"12"},"1529ae1888":{"L":"10","XL":"11","XXL":"12"}}"
    orders = json.loads(orders)
    for o in orders:
        qtys = frappe.get_all('Quantity Per Size', filters={
                              'order_id': o}, fields=['name', 'size', 'quantity'])
        for q in qtys:
            if(orders[o][q['size']] != q['quantity']):
                frappe.db.set_value('Quantity Per Size', q.name, {
                    'quantity': orders[o][q['size']]
                })
        order = frappe.get_doc('Sales Order Item', o)
        order.docstatus = 1
        order.save()
    frappe.db.commit()
    return {'status': 'ok'}


@frappe.whitelist()
def modify_sales_item_orders(orders_object):
    # order_object is in following format
    # {
    #     "sales_item_order":
    #         {
    #             "M":2,
    #             "XL":3
    #         }
        
    # }
    order_dic = json.loads(orders_object)
    for order in order_dic:
        frappe.db.set_value('Sales Order Item', order, {
            'docstatus': 0
        })
        update_item_quantities(order,order_dic[order])

    return {'status': 'ok'}

@frappe.whitelist()
def cancel_sales_item_orders(item_order_list):
    item_order_list = ast.literal_eval(item_order_list)
    for item_order in item_order_list:
        order = frappe.get_doc('Sales Order Item', item_order)
        order.docstatus = 1
        order.save()
        order.docstatus = 2
        order.save()
        frappe.db.commit()
    return {'status': 'ok'}


@frappe.whitelist()
def validate_sales_item_orders(orders_object):
    # order_object is in following format
    # {
    #     "sales_item_order":
    #         {
    #             "M":2,
    #             "XL":3
    #         }
        
    # }
    order_dic = json.loads(orders_object)
    for order in order_dic:
        update_item_quantities(order,order_dic[order])
        frappe.db.set_value('Sales Order Item', order, {
            'docstatus': 1
        })
        frappe.db.commit()
        sales_order_item=frappe.get_doc('Sales Order Item',order)
        item=sales_order_item.item_code
        destination=sales_order_item.item_destination
        
        makeProductionOrder(item,order,destination)

    return {'status': 'ok'}

def makeProductionOrder(item_name,sales_order_item_name,destination):

    item=frappe.get_doc("Item",item_name)
    fabSuppliers={}
    trimSuppliers={}
    packSuppliers={}
    
    for supplier in item.supplier:
        if(supplier.supplier_group=='Fabric'):
           
            fabSuppliers[random.random()]={
                'fabric_supplier': supplier.supplier,
                'fabric_ref': supplier.fabric_ref,
                'fabric_con': supplier.fabric_consumption,
                'fabric_status':''
                
            }
        elif(supplier.supplier_group=='Trimming'):
            trimSuppliers[random.random()]={
                'trim_supplier': supplier.supplier,
                'trim_ref': supplier.trimming_ref,
                'trim_con': supplier.trimming_consumption,
                'trim_status':''
                
            }
        elif(supplier.supplier_group=='Packaging'):
            packSuppliers[random.random()]={
                'pack_supplier': supplier.supplier,
                'pack_ref': supplier.packaging_ref,
                'pack_con': supplier.packaging_consumption,
                'pack_status':''
                
            }
            
    quantities=frappe.get_all('Quantity Per Size',filters={'order_id':sales_order_item_name,'product_id':item_name},fields=['size','quantity'])
    production_order={
        'product_category':item.item_group,
        'internal_ref':'SOI-'+sales_order_item_name,
        'product_name':item.name,
        'production_factory':'Test Factory',     #need to set factory from sales order validation page
        'final_destination':destination,
        'quantity':quantities,
        'fab_suppliers':fabSuppliers,
        'trim_suppliers':trimSuppliers,
        'pack_suppliers':packSuppliers,
        'comment':''
    }

    create_production_order(json.dumps(production_order))


