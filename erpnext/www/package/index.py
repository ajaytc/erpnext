from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime


def get_context(context):
    if frappe.session.user == 'Guest':
        frappe.throw(
            _("You need to be logged in to access this page"), frappe.PermissionError)
    roles = frappe.get_roles(frappe.session.user)

    if ("Administrator" not in roles) and ("Brand User" not in roles):
        frappe.throw(_("Not Permitted!"), frappe.PermissionError)

    brand = frappe.get_doc('User', frappe.session.user).brand_name

    pricing_details = frappe.get_all('Client Pricing', filters={'brand': brand,'docstatus':0}, fields=['client','item_group','item_code'])
    context.clients = {}
    support_itemgroup_dic, support_itemcode_dic = fill_suport_dics(pricing_details)

    for pricing in pricing_details:
        if pricing.client not in context.clients:
            context.clients[pricing.client] = []
        pricing["item_name"] = support_itemcode_dic[pricing.item_code]
        pricing["item_group_name"] = support_itemgroup_dic[pricing.item_group]
        context.clients[pricing.client].append(pricing)

    for client in context.clients:
        x = context.clients[client]
        context.clients[client] = set_cats_prods(x,client,brand)

    return context

def fill_suport_dics(pricing_details):
    item_groups ={}
    item_codes = {}
    for pricing in pricing_details:
        if pricing.item_code not in item_codes:
            temp_itemname = frappe.get_all('Item', filters={'name':pricing.item_code}, fields=['item_name'])
            if len(temp_itemname)!=0:
                item_codes[pricing.item_code] = temp_itemname[0].item_name
            else:
                item_codes[pricing.item_code] = pricing.item_code

        if pricing.item_group not in item_groups:
            temp_itemgroup = frappe.get_all('Item Group', filters={'name':pricing.item_group}, fields=['item_group_name'])
            if len(temp_itemgroup)!=0:
                item_groups[pricing.item_group] = temp_itemgroup[0].item_group_name
            else:
                item_groups[pricing.item_group] = pricing.item_group
    return item_groups,item_codes

def set_cats_prods(prod_list,client,brand):
    temp_prods = {}
    temp_client = {}
    for prods in prod_list:
        if prods.item_group not in temp_prods:
            temp_prods[prods.item_group] = {}
            temp_prods[prods.item_group]["item_group_name"] = prods.item_group_name
            temp_prods[prods.item_group]["products"] = {}
        if prods.item_code not in temp_prods[prods.item_group]["products"]:
            temp_prods[prods.item_group]["products"][prods.item_code] = prods.item_name
    c_data = frappe.get_all('Customer', filters={'brand': brand,'name':client}, fields=['customer_name'])
    if (len(c_data)==0):
        temp_client["client_name"] = client
    else:
        temp_client["client_name"] = c_data[0].customer_name

    temp_client["client"] = client
    temp_client["prod_cats"] = temp_prods
    return temp_client
    