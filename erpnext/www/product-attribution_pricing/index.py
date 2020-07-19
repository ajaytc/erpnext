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
    context.clients = frappe.get_all('Customer', filters={'brand': brand}, fields=['name'])
    context.product_cats = frappe.get_all('Item Group', filters={'brand_name': brand}, fields=['name'])
    if (len(context.product_cats)!=0):
        context.items = frappe.get_all('Item', filters={'item_group':context.product_cats[0].name, 'brand':brand}, fields=['item_name','name'])
    else:
        context.items=[]
    return context
