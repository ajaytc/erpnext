import frappe
import json
import ast
import random
from erpnext.modehero.production import create_production_order
from erpnext.modehero.product import get_sizing_scheme
from erpnext.modehero.supplier import get_supply_doc
from erpnext.modehero.stock import get_stock
from erpnext.modehero.fabric import create_fabric_order
from erpnext.modehero.trimming import create_trimming_order
from erpnext.modehero.package import create_packaging_order
from frappe.email.doctype.notification.notification import sendCustomEmail


@frappe.whitelist()
def create_sales_order(items, garmentlabel, internalref, profoma):
    prepared = []
    items = json.loads(items)
    for i in items:
        free_size_qty = None
        if items[i]['free_size_qty'] != None and get_sizing_scheme(items[i]['item'])==None:
            free_size_qty = int(items[i]['free_size_qty']) if is_number(items[i]['free_size_qty']) else 0
        prepared.append({
            "item_name": items[i]['item'],
            "item_code": items[i]['item'],
            "qty": 1,
            "rate": 1,
            "warehouse": "",
            "uom": "pcs",
            "conversion_factor": 1,
            "item_destination": items[i]['destination'],
            "free_size_qty": free_size_qty,
            "first_free_size_qty":free_size_qty
        })

    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    customer = frappe.get_all(
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


@frappe.whitelist(allow_email_guest=True)
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
    status = "ok"
    for order in order_dic:
        try:
            order_doc = frappe.get_doc('Sales Order Item', order)
            if order_doc.free_size_qty!=None and order_doc.first_free_size_qty!=None:
                order_doc.free_size_qty = order_dic[order]["sizes"]["Free Size"]
                order_doc.is_modified = 1
                order_doc.save()
                frappe.db.commit()
            else:
                update_item_quantities(order,order_dic[order]["sizes"])
            sendCancelNModifyNotificationEmail(order_doc,'Modified')
        except Exception:
            status = "error"
            continue
    return {'status': status}

@frappe.whitelist()
def cancel_sales_item_orders(item_order_list):
    item_order_list = ast.literal_eval(item_order_list)
    one_of_oder_name = ""
    if len(item_order_list)>0 : one_of_oder_name = item_order_list[0]
    for item_order in item_order_list:
        order = frappe.get_doc('Sales Order Item', item_order)
        order.docstatus = 1
        order.save()
        order.docstatus = 2
        order.group_no = one_of_oder_name
        order.save()
        frappe.db.commit()
        sendCancelNModifyNotificationEmail(order,'Product Cancelled')
    return {'status': 'ok'}

def sendCancelNModifyNotificationEmail(order_item,trigger):
    sales_order=frappe.get_doc('Sales Order',order_item.parent)
    customer=frappe.get_doc('Customer',sales_order.customer)
    recipient=frappe.get_doc('User',sales_order.owner)

    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name


    notification=frappe.get_doc("Notification","Supply/Purchase Order Cancel/Modify")

    templateData={}
    templateData['recipient_name']=customer.customer_name
    templateData['SNF']=brand
    templateData['trigger']=trigger
    templateData['internal_ref']=sales_order.internal_ref
    # templateData['brand']=sales_order.brand
    templateData['order_date']=sales_order.creation.date()
    templateData['order_link']='new-client-order?order='+sales_order.name+'&amp;sk=1'
    # templateData['order_type']=orderType
    # templateData['order_name']=sales_order.name
    templateData['recipient']=customer.email_address
    templateData['lang']=recipient.language
    templateData['notification']=notification

    # new-client-order?order=SAL-ORD-2020-00048

    if(customer.email_address != None):
        sendCustomEmail(templateData)

@frappe.whitelist()
def validate_products_supply(sales_orders,supply_orders):
    # try except is used in supply order creation and production order creation because, the final message is important to customer.
    supply_orders = json.loads(supply_orders)
    # lets create the suppy order first because the use input of the supply order is higher and the prtob of having a error higher
    supply_order_result = create_supply_orders(supply_orders)
    production_order_result = validate_products_only(sales_orders)
    message = production_order_result["message"] + supply_order_result["message"]
    if (supply_order_result["status"]=="ok" and production_order_result["status"]=="ok"):
        return {"status":"ok","message":message}
    return {"status":"error","message":message}

def create_supply_orders(supply_orders):
    # {
    #     "supply_ref_1":{
    #                     "supply_group":"fabric",
    #                     "destination_1":{
    #                                         "vendor_1":{
    #                                                         "total_count":23,
    #                                                         "bla bla":"bla"
    #                                                     }
    #                                     }
    #                     },
    #     "supply_ref_2":............
    # }
    successfull_supply_order_internal_refs = []
    unsuccessfull_supply_order_internal_refs = []
    result_message = ""
    is_completed = "error"
    supply_order_data_list,total_order_count = collect_data_for_supply_order(supply_orders)
    for supply_order_data in supply_order_data_list:
        created_order = None
        try:
            created_order = create_supply_order_by_category(supply_order_data)
            if (created_order["status"]=="ok"):
                successfull_supply_order_internal_refs.append(created_order["order"].internal_ref)
        except Exception:
            unsuccessfull_supply_order_internal_refs.append(supply_order_data["internal_ref"])
            continue
    if (total_order_count==len(successfull_supply_order_internal_refs)):
        is_completed = "ok"
        result_message = "All supply orders created sucessfully !"
    else:
        result_message = "Supply order creation unsuccessfull. From requested internal refs,"+ str(len(unsuccessfull_supply_order_internal_refs)) +" internal refs' orders are not created !"
    return { "status":is_completed, "message":result_message }

def create_supply_order_by_category(supply_order_data):
    if (supply_order_data["supply_group"]=="fabric"):
        return create_fabric_order(supply_order_data)
    elif (supply_order_data["supply_group"]=="trimming"):
        return create_trimming_order(supply_order_data)
    elif (supply_order_data["supply_group"]=="packaging"):
        return create_packaging_order(supply_order_data)
    else : 
        return {"status":"error"}

def collect_data_for_supply_order(supply_data):
    supply_order_data_list = []
    count = 0
    for supply_ref in supply_data:
        supply_doc = get_supply_doc(supply_ref,supply_data[supply_ref]["supply_group"])
        stock_doc = get_stock(supply_data[supply_ref]["supply_group"],supply_ref)
        for destination_ref in supply_data[supply_ref]["destinations"]:
            for vendor_ref in supply_data[supply_ref]["destinations"][destination_ref]:
                count = count + 1
                order_count =  str(supply_data[supply_ref]["destinations"][destination_ref][vendor_ref]["order_count"]).strip()
                if not(len(supply_data[supply_ref]["destinations"][destination_ref][vendor_ref]["internal_ref"].strip())!=0 and len(destination_ref.strip())!=0 and is_vendor_allowed(vendor_ref)  and supply_doc!=None and order_count.isnumeric() ):
                    continue
                unit_price = str(supply_doc.unit_price).strip()
                if not(is_number(unit_price)):
                    continue
                data_dictionary = supply_data[supply_ref]["destinations"][destination_ref][vendor_ref]
                data_obj = {
                    "in_stock" : stock_doc["quantity"],
                    "price_per_unit":unit_price,
                    "production_factory":destination_ref,
                    "supply_group":supply_data[supply_ref]["supply_group"],
                    "minimum_order_quanity":supply_doc.minimum_order_qty,
                    "total_price": float(unit_price)*int(order_count),
                    "internal_ref":data_dictionary["internal_ref"],
                    "quantity":order_count,
                    "profoma_reminder":data_dictionary["reminder"]["proforma_date"],
                    "confirmation_reminder":data_dictionary["reminder"]["confirmation_date"],
                    "payment_reminder":data_dictionary["reminder"]["payment_date"],
                    "reception_reminder":data_dictionary["reminder"]["reception_date"],
                    "shipment_reminder":data_dictionary["reminder"]["shipment_date"]
                }
                data_obj_with_product_attribute = set_product_attribute_of_supply_order(data_dictionary["products"],data_obj)
                if data_obj_with_product_attribute==None:
                    continue
                data_obj = data_obj_with_product_attribute
                if (supply_data[supply_ref]["supply_group"]=="fabric"):
                    data_obj["fabric_ref"] = supply_ref
                    data_obj["fabric_vendor"] = vendor_ref
                elif (supply_data[supply_ref]["supply_group"]=="packaging"):
                    data_obj["packaging_item"] = supply_ref
                    data_obj["packaging_vendor"] = vendor_ref
                elif (supply_data[supply_ref]["supply_group"]=="trimming"):
                    data_obj["trimming_item"] = supply_ref
                    data_obj["trimming_vendor"] = vendor_ref
                else:
                    continue
                supply_order_data_list.append(data_obj)
    return supply_order_data_list,count

def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def set_product_attribute_of_supply_order(data_product,full_data_obj):
    if not type(data_product) is list:
        return None
    if len(data_product)==1 and data_product[0]!="" and data_product[0]!=None :
        full_data_obj["item_code"] = data_product[0]
    elif len(data_product)>1:
        temp_p_list = []
        for product in data_product:
            if product!=None and product!="":
                temp_p_list.append({"product":product})
        if len(temp_p_list)!=len(data_product):
            return None
        full_data_obj["item_code"]=None
        full_data_obj["item_list"] = temp_p_list
    else:
        return None
    return full_data_obj
    

@frappe.whitelist()
def validate_products_only(order_bloc_object):
    # {
    #     "item_name1":{
    #         "factory_details":"12345",
    #         "order":
    #             {
    #                 "sales_item_order1":{},
    #                 "sales_itm_order2":{}
    #             }
    #     }
    # }
    order_bloc_object_dic = json.loads(order_bloc_object)
    requested_item_count = len(order_bloc_object_dic)
    successfull_items = []
    result_message=""
    for item in order_bloc_object_dic:
        if not(is_allowed_factory(order_bloc_object_dic[item]["factory"])) or not(is_allowed_product(item)):
            continue
        try:
            result = validate_sales_item_orders_n_create_production_order(order_bloc_object_dic[item]["order"],order_bloc_object_dic[item]["factory"])
            successfull_items.append(item)
        except Exception:
            continue
    if requested_item_count==len(successfull_items):
        result_message = "Sales orders validated and production order created successfully !"
        return {"status":"ok", "message":result_message}
    else:
        result_message = "Sales orders valdiation and prouction order creation is not completed. "
        # for item in successfull_items:
        #     result_message = result_message + " '"+item+"' "
        # result_message = result_message + " item's sales orders validated and production orders created successfully !"
        return {"status":"error" , "message":result_message}
        

def validate_sales_item_orders_n_create_production_order(orders_object,factory):
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
    quantity_dic_for_production_order,item,destinations_comment,one_of_sales_order_item_names,free_size_qty= collect_sales_order_data_for_production_order(order_dic)
    production_order_ref = makeProductionOrder(item,one_of_sales_order_item_names,destinations_comment,quantity_dic_for_production_order,factory,free_size_qty).name
    update_sales_order_items(production_order_ref,order_dic,one_of_sales_order_item_names)
    return {'status': 'ok'}

def update_sales_order_items(production_order_ref,order_dic,one_of_sales_order_item_names):
    for order in order_dic:
        frappe.db.set_value('Sales Order Item', order, {
            'docstatus': 1,
            'prod_order_ref':production_order_ref,
            'group_no':one_of_sales_order_item_names
        })
    frappe.db.commit()

def collect_sales_order_data_for_production_order(order_dic):
    quantity_dic_for_production_order = {}
    item = None
    destinations_comment = ""
    one_of_sales_order_item_names = ""
    free_size_qty = None
    for order in order_dic:
        if (one_of_sales_order_item_names==""):
            one_of_sales_order_item_names = order
        # update_item_quantities(order,order_dic[order]["sizes"])
        sales_order_item=frappe.get_doc('Sales Order Item',order)  
        if (item==None):
            item=sales_order_item.item_code
        elif(item!=sales_order_item.item_code):
            return {'status':'Different products error'}
        if sales_order_item.free_size_qty!=None and sales_order_item.first_free_size_qty!=None:
            if free_size_qty==None:
                free_size_qty = 0  
            free_size_qty = free_size_qty + int(sales_order_item.free_size_qty) if is_number(sales_order_item.free_size_qty) else 0
            item_quantites = []
        else:
            item_quantites = frappe.get_all('Quantity Per Size',filters={'order_id':order},fields=['name','size','quantity'])
        for quantity in item_quantites:
            if (quantity['size'] not in quantity_dic_for_production_order):
                quantity_dic_for_production_order[quantity['size']] = 0
            quantity_dic_for_production_order[quantity['size']] = quantity_dic_for_production_order[quantity['size']] + int(quantity['quantity'])
        destinations_comment = destinations_comment + str(order_dic[order]["client_name"])+" : "+str(sales_order_item.item_destination)+" \n "
    return quantity_dic_for_production_order,item,destinations_comment,one_of_sales_order_item_names,free_size_qty
    
def makeProductionOrder(item_name,one_of_sales_order_item_names,destinations_comment,quantity_dic_for_production_order,factory,free_size_qty):

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
        'production_factory':factory,     #need to set factory from sales order validation page
        'final_destination': None,       #many final destinations for different clients and its comlicated
        'quantity':format_quantity_dic(quantity_dic_for_production_order),
        'fab_suppliers':fabSuppliers,
        'trim_suppliers':trimSuppliers,
        'pack_suppliers':packSuppliers,
        'comment':destinations_comment,
        'free_size_qty':free_size_qty,
        'destination_type':None
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

def is_vendor_allowed(vendor_ref) :
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    if len(frappe.get_all("Brand Suppliers",{"parent":vendor_ref,"brand":brand}))!=0:
        return True
    return False
def is_allowed_factory(factory):
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    if len(frappe.get_all("Brand Factory",{"parent":factory,"brand":brand}))!=0:
        return True
    return False
def is_allowed_product(item):
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    if len(frappe.get_all("Item",{"name":item,"brand":brand}))!=0:
        return True
    return False
