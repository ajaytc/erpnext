from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime

no_cache = 1


def get_context(context):
    if frappe.session.user == 'Guest':
        frappe.throw(
            _("You need to be logged in to access this page"), frappe.PermissionError)
    roles = frappe.get_roles(frappe.session.user)

    if ("System Manager" in roles):
        context.user_type = "System"
    elif ("Brand User" in roles):
        context.user_type = "Brand"
    elif ("Customer" in roles):
        context.user_type = "Customer"
    else:
        frappe.throw(_("Not Permitted!"), frappe.PermissionError)

    brand = frappe.get_doc('User', frappe.session.user).brand_name
    if (context.user_type == "Brand" or context.user_type == "System"):
        orders = frappe.get_all('Sales Order', filters={'company': brand}, fields=['name', 'customer'])
    else:
        orders = frappe.get_list('Sales Order', filters={'company': brand, 'owner':frappe.session.user}, fields=['name', 'customer'])

    support_client_dic = collect_client_data(orders)

    order_items = {}
    for o in orders:
        order_items[o.name] = frappe.get_list('Sales Order Item',filters={'parent':o.name,'docstatus':['!=',0]},fields=['name','item_code','parent','creation','modified','is_modified','docstatus','prod_order_ref'])

        for sales_order_item_index in range(len(order_items[o.name])):
            order_items[o.name][sales_order_item_index]["customer_details"] = support_client_dic[o.customer]
    item_orders =  sort_item_doc(get_unique_items_orders(order_items))

    context.unique_items_orders = seperate_item_orders_by_production_orders(item_orders)

    return context

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
        if order.customer in temp_clients:
            continue
        temp_clients.append(order.customer)
        cus_db_data = frappe.get_all('Customer',{'name':order.customer},['customer_name','name','city','country','email_address','phone'])
        if (len(cus_db_data)==0):
            client_object[order.customer] = {'customer_name':None,'name':order.customer,'city':None,'country':None,'email_address':None,'phone':None}
            continue
        client_object[order.customer] = cus_db_data[0]
    return client_object

def seperate_item_orders_by_production_orders(item_orders):
    temp_result_dic = {}
    for item in item_orders:
        if item not in temp_result_dic:
            temp_result_dic[item] = {}
            temp_result_dic[item]["item_name"] = item_orders[item]["item_name"]
            temp_result_dic[item]["orders"] = {}
        for order in item_orders[item]["orders"]:
            if order.prod_order_ref not in temp_result_dic[item]["orders"]:
                temp_result_dic[item]["orders"][order.prod_order_ref] = {"prod_order_status":None,"client_orders":[]}
                try:
                    temp_result_dic[item]["orders"][order.prod_order_ref]["prod_order_status"] = frappe.get_doc('Production Order',order.prod_order_ref).docstatus
                except Exception:
                    pass
            temp_result_dic[item]["orders"][order.prod_order_ref]["client_orders"].append(order)
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
