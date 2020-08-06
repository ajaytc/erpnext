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

    if ("Administrator" not in roles) and ("Brand User" not in roles):
        frappe.throw(_("Not Permitted!"), frappe.PermissionError)

    brand = frappe.get_doc('User', frappe.session.user).brand_name
    orders = frappe.get_all('Sales Order', filters={'company': brand}, fields=['name', 'customer'])
    support_client_dic = collect_client_data(orders)

    order_items = {}
    for o in orders:
        order_items[o.name] = frappe.get_list('Sales Order Item',filters={'parent':o.name,'docstatus':0},fields=['name','item_code','parent','creation','modified'])
        for sales_order_item_index in range(len(order_items[o.name])):
            order_items[o.name][sales_order_item_index]["customer_details"] = support_client_dic[o.customer]
    
    context.unique_items_orders = get_unique_items_orders(order_items)
    return context

## returns unique item objects
def get_unique_items_orders(order_items):
    temp_codes = []
    temp_objects = {}
    for order in order_items:
        for item in order_items[order]: 
            if item.item_code in temp_codes:
                temp_objects[item.item_code].append(item)
                continue
            temp_codes.append(item.item_code)
            temp_objects[item.item_code] = []
            temp_objects[item.item_code].append(item)
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