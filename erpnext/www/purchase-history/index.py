from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime
from erpnext.modehero.user import haveAccess
from erpnext.modehero.dispatch_bulk import collect_item_destination_data,add_size_quantity_data,add_sent_data,modify_order_list

no_cache = 1


def get_context(context):
    module='client'
    if frappe.session.user == 'Guest':
        frappe.throw(
            _("You need to be logged in to access this page"), frappe.PermissionError)
    
    if(not haveAccess(module)):
        frappe.throw(
            _("You have not subscribed to this service"), frappe.PermissionError)
    roles = frappe.get_roles(frappe.session.user)
    brand = frappe.get_doc('User', frappe.session.user).brand_name
    params = frappe.form_dict
    orders,context.user_type = get_orders(roles,brand,frappe.session.user,params)
    support_client_dic = collect_client_data(orders)
    order_items = add_sales_order_details(support_client_dic,orders,params)
    item_orders =  sort_item_doc(get_unique_items_orders(order_items))
    context.unique_items_orders = seperate_item_orders_by_production_orders(item_orders)
    if context.user_type == "Brand" :
        context.bulk_orders,context.bulk_index_dic = get_bulk_orders(brand,params)
    return context

def add_sales_order_details(support_client_dic,orders,params):
    order_items = {}
    for o in orders:
        order_items[o["name"]] = []
        if "destination" in params :
            order_items[o["name"]] = frappe.get_list('Sales Order Item',filters={'parent':o["name"],'docstatus':['!=',0],'item_destination':params.destination},fields=['name','item_code','parent','creation','modified','is_modified','docstatus','prod_order_ref','group_no'])
        else:
            order_items[o["name"]] = frappe.get_list('Sales Order Item',filters={'parent':o["name"],'docstatus':['!=',0]},fields=['name','item_code','parent','creation','modified','is_modified','docstatus','prod_order_ref','group_no'])

        for sales_order_item_index in range(len(order_items[o["name"]])):
            order_items[o["name"]][sales_order_item_index]["customer_details"] = support_client_dic[o.customer]
    return order_items

def get_orders(roles,brand,session_user,params):
    if ("System Manager" in roles):
        user_type = "System"
    elif ("Brand User" in roles):
        user_type = "Brand"
    elif ("Customer" in roles):
        user_type = "Customer"
    else:
        frappe.throw(_("Not Permitted!"), frappe.PermissionError)

    orders = []
    if (user_type == "Brand" or user_type == "System") and ("destination" in params):
        temps = []
        destination = params.destination
        orders_sql = frappe.db.sql("""select so.name,so.customer,soi.item_destination,soi.parent from `tabSales Order` so left join `tabSales Order Item`soi on soi.parent=so.name  where soi.item_destination=%s and so.company=%s """, (destination,brand))
        for order in orders_sql:
            if order[0] in temps: continue
            temps.append(order[0])
            orders.append({"name":order[0],"customer":order[1]})
    elif(user_type == "Brand" or user_type == "System") and ("client" in params):
        client = params.client
        orders = frappe.get_all('Sales Order', filters={'company': brand, 'customer':client}, fields=['name', 'customer'])
    elif(user_type == "Brand" or user_type == "System") and ("pos" in params):
        orders = []
    else:
        orders = frappe.get_all('Sales Order', filters={'company': brand, 'owner':session_user}, fields=['name', 'customer'])
    return orders,user_type
## returns unique item objects
def get_unique_items_orders(order_items):
    temp_codes = []
    temp_objects = {}
    for order in order_items:
        for item in order_items[order]: 
            if item.item_code in temp_codes:
                temp_objects[item.item_code]["orders"].append(item)
                continue
            temp_codes.append(item.item_code)
            item_name = frappe.get_all('Item',{'item_code':item.item_code},'item_name')
            if (len(item_name)!=0):
                item_name = item_name[0].item_name
            else:
                item_name = ""
            temp_objects[item.item_code] = {"item_name":item_name}
            temp_objects[item.item_code]["orders"]=[]
            temp_objects[item.item_code]["orders"].append(item)
    return temp_objects

def collect_client_data(orders):
    temp_clients = []
    client_object = {}
    for order in orders:
        if order["customer"] in temp_clients:
            continue
        temp_clients.append(order["customer"])
        cus_db_data = frappe.get_all('Customer',{'name':order["customer"]},['customer_name','name','city','country','email_address','phone'])
        if (len(cus_db_data)==0):
            client_object[order["customer"]] = {'customer_name':None,'name':order["customer"],'city':None,'country':None,'email_address':None,'phone':None}
            continue
        client_object[order["customer"]] = cus_db_data[0]
    return client_object

def seperate_item_orders_by_production_orders(item_orders):
    temp_result_dic = {}
    for item in item_orders:
        if item not in temp_result_dic:
            temp_result_dic[item] = {}
            temp_result_dic[item]["item_name"] = item_orders[item]["item_name"]
            temp_result_dic[item]["orders"] = {}
        for order in item_orders[item]["orders"]:
            if order.group_no not in temp_result_dic[item]["orders"]:
                temp_result_dic[item]["orders"][order.group_no] = {"prod_order_status":None,"client_orders":[]}
                try:
                    temp_result_dic[item]["orders"][order.group_no]["prod_order_status"] = frappe.get_doc('Production Order',order.prod_order_ref).docstatus
                except Exception:
                    pass
            temp_result_dic[item]["orders"][order.group_no]["client_orders"].append(order)
    return temp_result_dic


def sort_item_doc(item_doc):
    result_doc = {}
    string_list = []
    for item in item_doc:
        if item_doc[item]["item_name"] in string_list:
            continue
        string_list.append(item_doc[item]["item_name"])
    string_list = sorted(string_list,key=str.lower)
    for item_name in string_list:
        for item in item_doc:
            if item_doc[item]["item_name"]==item_name:
                result_doc[item] = item_doc[item]
                break
    return result_doc

def get_bulk_orders(brand,params):
    orders = frappe.db.sql("""select soi.name,po.name,po.destination_type,soi.item_destination,po.final_destination,po.product_name,po.production_factory,po.carrier,po.tracking_number,po.shipment_date,po.creation,soi.creation,po.internal_ref,soi.parent from `tabProduction Order` po left join `tabSales Order Item`soi on po.name=soi.prod_order_ref and soi.docstatus in (%s,%s) where po.brand=%s and po.docstatus in (%s,%s,%s)  order by po.creation desc""", ("2","3",brand,"1","2","3"))
    index_doc = get_index_doc()
    orders = list(orders)
    for i in range(len(orders)):
        orders[i] = list(orders[i])
    orders = get_history_orders(orders,params)
    pos_destination_support_data,item_support_data = collect_item_destination_data(orders)
    orders_with_quantity_data = add_size_quantity_data(orders,item_support_data)
    final_order_list = add_sent_data(orders_with_quantity_data,brand)
    result = modify_order_list(final_order_list,pos_destination_support_data)
    return result,index_doc

def get_index_doc():
    index_doc = {}
    # 0 = sales_order_item_name
    index_doc["soi_name_index"]= 0
    # 1 = production_order_name
    # 2 = production_order_destination_type
    # 3 = sales_order_item_destination
    # 4 = production_order_destiantion
    # 5 = product_name
    # 6 = production_factory
    # 7 = carrier_number
    # 8 = tracking_number
    # 9 = shipment_date
    # 10 = po_creation_time
    index_doc["po_creation_time_index"] = 10
    # 11 = soi_creation_time
    index_doc["soi_creation_time_index"] = 11
    # 12 = po_internal_ref
    index_doc["if_index"] = 12
    # 13 = soi_parent_name
    index_doc["soi_parent_index"] = 13
    # 14 = item_name
    index_doc["item_name_index"] = 14
    # 15 = item_sizes
    index_doc["sizes_scheme_index"] = 15
    # 16 = current_stock_sizes_quantities
    index_doc["stock_qty_index"] = 16
    # 17 = order_size_details
    index_doc["order_qty_index"] = 17
    # 18 = sent_history
    index_doc["sent_history_index"] = 18
    # 19 = current_active_shipment 
    index_doc["current_active_shipment_index"] = 19
    # 20 = POS_or_DESTINY
    # 21 = is_tickable
    index_doc["is_tickable_index"] = 21
    return index_doc

def get_history_orders(orders,params):
    result = []
    for order in orders:
        if order[0]!=None:
            if "pos" in params:
                continue
            elif "client" in params:
                if len(frappe.get_all('Sales Order', filters={"name":order[13],'customer':params.client}))==0:
                    continue
            else:
                continue
            result.append(order)
        else:
            porder = frappe.get_doc("Production Order",order[1])
            if "pos" in params:
                if not (params.pos==order[4] and order[2]=="1"):
                    continue
            elif "client" in params:
                # if order[2]=="1":
                #     if len(frappe.get_all('Point Of Sales',{"name":order[4],'parent_company':params.client}))==0:
                #         continue
                if order[2]=="0":
                    if len(frappe.get_all('Destination',{"name":order[4],'client_name':params.client}))==0:
                        continue
                else:
                    continue
            else:
                continue
            if porder.docstatus==2 or porder.docstatus==3:
                result.append(order)
    return result

    