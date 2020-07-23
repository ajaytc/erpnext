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
    context.active_products = frappe.get_all('Client Pricing', filters={'brand': brand,'docstatus':0}, fields=['name','client','season','item_code','item_group'],order_by= 'creation desc')
    k = len(context.active_products)
    for cp in range(k):
        iname = frappe.get_all('Item',filters={'name':context.active_products[cp].item_code},fields=['item_name'])[0].item_name
        igroup = frappe.get_all('Item Group',filters={'name':context.active_products[cp].item_group},fields=['item_group_name'])[0].item_group_name
        context.active_products[cp]["item_name"] = iname
        context.active_products[cp]["item_group_name"] = igroup

    return context
