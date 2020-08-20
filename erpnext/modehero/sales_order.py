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
        frappe.db.set_value('Sales Order Item', sales_order_item_name, {
            'is_modified': "1"
        })
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
    #     {
    #         "sizes":
    #         {
    #             "M":2,
    #             "XL":3
    #         }
    #     }
    #}
    order_dic = json.loads(orders_object)
    for order in order_dic:
        update_item_quantities(order,order_dic[order]["sizes"])

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
def validate_products_only(order_bloc_object):
    # {
    #     "item_name1":
    #     "factory_details":"12345",
    #     "order":
    #         {
    #             "sales_item_order1":{},
    #             "sales_itm_order2":{}
    #         }
    # }
    try:
        order_bloc_object_dic = json.loads(order_bloc_object)
        for item in order_bloc_object_dic:
            result = validate_sales_item_orders(order_bloc_object_dic[item]["order"])
            if (result["status"]!="ok"):
                break
        else:
            return {"status":"ok"}
    except:
        return {"status":"error"}

@frappe.whitelist()
def validate_sales_item_orders(orders_object):
    # order_object is in following format
    # {
    #     "sales_item_order":
    #     {
    #         "client_name": "name of the client"
    #         "sizes":
    #         {
    #             "M":2,
    #             "XL":3
    #         }
    #     }
    #}
    if not(isinstance(orders_object, dict)):
        order_dic = json.loads(orders_object)
    else:
        order_dic = orders_object
    quantity_dic_for_production_order,item,destinations_comment,one_of_sales_order_item_names = collect_vaidation_form_data(order_dic)
    production_order_ref = makeProductionOrder(item,one_of_sales_order_item_names,destinations_comment,quantity_dic_for_production_order).name
    update_sales_order_items(production_order_ref,order_dic)
    return {'status': 'ok'}

def update_sales_order_items(production_order_ref,order_dic):
    for order in order_dic:
        frappe.db.set_value('Sales Order Item', order, {
            'docstatus': 1,
            'prod_order_ref':production_order_ref
        })
    frappe.db.commit()


def collect_vaidation_form_data(order_dic):
    quantity_dic_for_production_order = {}
    item = None
    destinations_comment = ""
    one_of_sales_order_item_names = ""
    for order in order_dic:
        if (one_of_sales_order_item_names==""):
            one_of_sales_order_item_names = order
        # update_item_quantities(order,order_dic[order]["sizes"])
        sales_order_item=frappe.get_doc('Sales Order Item',order)  
        if (item==None):
            item=sales_order_item.item_code
        elif(item!=sales_order_item.item_code):
            return {'status':'Different products error'}

        item_quantites = frappe.get_all('Quantity Per Size',filters={'order_id':order},fields=['name','size','quantity'])
        for quantity in item_quantites:
            if (quantity['size'] not in quantity_dic_for_production_order):
                quantity_dic_for_production_order[quantity['size']] = 0
            quantity_dic_for_production_order[quantity['size']] = quantity_dic_for_production_order[quantity['size']] + int(quantity['quantity'])
        destinations_comment = destinations_comment + str(order_dic[order]["client_name"])+" : "+str(sales_order_item.item_destination)+" \n "
    return quantity_dic_for_production_order,item,destinations_comment,one_of_sales_order_item_names
    
def makeProductionOrder(item_name,one_of_sales_order_item_names,destinations_comment,quantity_dic_for_production_order):

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
            
    # quantities=frappe.get_all('Quantity Per Size',filters={'order_id':one_of_sales_order_item_names,'product_id':item_name},fields=['size','quantity'])
    production_order={
        'product_category':item.item_group,
        'internal_ref':'SOI-'+one_of_sales_order_item_names,
        'product_name':item.name,
        'production_factory':'Test Factory',     #need to set factory from sales order validation page
        'final_destination': None,       #many final destinations for different clients and its comlicated
        'quantity':format_quantity_dic(quantity_dic_for_production_order),
        'fab_suppliers':fabSuppliers,
        'trim_suppliers':trimSuppliers,
        'pack_suppliers':packSuppliers,
        'comment':destinations_comment
    }

    prod_order =  create_production_order(json.dumps(production_order))
    return prod_order['order']


def format_quantity_dic(quantit_dic):
    result_array = []
    for size in quantit_dic:
        result_array.append({"size":size,"quantity":str(quantit_dic[size])})
    return result_array

@frappe.whitelist()
def get_total_products(order_list):
    order_list =  ast.literal_eval(order_list)
    total = 0
    for sales_order_item in order_list:
        item_quantites = frappe.get_all('Quantity Per Size',filters={'order_id':sales_order_item},fields=['quantity'])
        for quantty in item_quantites:
            total = total + int(quantty["quantity"])
    return total

