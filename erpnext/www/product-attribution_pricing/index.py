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

    params = frappe.form_dict
    if('attribution_pricing' not in params ):
        if ('new' in params):
            context.newable = True
        context.clients = frappe.get_all('Customer', filters={'brand': brand}, fields=['name','customer_name'])
        context.product_cats = frappe.get_all('Item Group', filters={'brand_name': brand}, fields=['name','item_group_name'])
        if (len(context.product_cats)!=0 and len(context.clients)!=0 ):
            priced_items_for_first_product = frappe.get_all('Client Pricing',filters={'item_group':context.product_cats[0].name,'brand':brand,'client':context.clients[0].name},fields=['item_code'])
            item_list = frappe.get_all('Item', filters={'item_group':context.product_cats[0].name, 'brand':brand}, fields=['item_name','name'])
            temp_list = []
            for x in priced_items_for_first_product:
                temp_list.append(x.item_code)
            temp_showing_items = []
            for x in item_list:
                if (x.name not in temp_list):
                    temp_showing_items.append(x)
            context.item_list = temp_showing_items
        else:
            context.item_list=[]
    else:
        context.modifiable = True
        context.attribution_pricing = frappe.get_doc('Client Pricing', params.attribution_pricing)
        context.clients = frappe.get_all('Customer', filters={'brand': brand,'name':context.attribution_pricing.client}, fields=['name','customer_name'])
        context.product_cats = frappe.get_all('Item Group', filters={'brand_name': brand,'name':context.attribution_pricing.item_group}, fields=['name','item_group_name'])
        context.item_list = frappe.get_all('Item', filters={'brand': brand,'name':context.attribution_pricing.item_code}, fields=['name','item_name'])
        
    return context
