from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime
from erpnext.modehero.user import haveAccess

no_cache = 1


def get_context(context):
    module = 'supply'
    if(not haveAccess(module)):
        frappe.throw(
            _("You have not subscribed to this service"), frappe.PermissionError)
    context.brand = frappe.get_doc("User", frappe.session.user).brand_name

    context.product_names = frappe.get_list(
        'Item', filters={'brand': context.brand}, fields=['item_name','item_code' ])
        
    context.packaging_items = frappe.get_list(
        'Packaging Item', filters={'brand': context.brand}, fields=['name'])

    context.production_facories = frappe.get_list(
        'Production Factory', filters={'brand': context.brand}, fields=['name','factory_name'])

    return context
