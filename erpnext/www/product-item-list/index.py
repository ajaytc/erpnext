import frappe
import json
import ast
import datetime
from frappe import _
from erpnext.modehero.user import haveAccess

def get_context(context):
    if frappe.session.user == 'Guest':
        frappe.throw(
            _("You need to be logged in to access this page"), frappe.PermissionError)
    module = 'production'
    if(not haveAccess(module)):
        frappe.throw(_("You have not subscribed to this service"),
                     frappe.PermissionError)
    roles = frappe.get_roles(frappe.session.user)

    if ("Brand User" not in roles):
        frappe.throw(_("Not Permitted!"), frappe.PermissionError)

    brand = frappe.get_doc('User', frappe.session.user).brand_name

    context.products = frappe.get_list('Item', filters={'brand': brand}, fields=[
                                       'item_name', 'item_group', 'name'])

    return context
