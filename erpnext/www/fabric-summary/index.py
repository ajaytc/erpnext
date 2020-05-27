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
    params = frappe.form_dict
    if('order' in params):
        context.fabricOrder = frappe.get_doc('Fabric Order', params.order)
        context.fabric=frappe.get_doc('Fabric',context.fabricOrder.fabric_ref);

    context.roles = frappe.get_roles(frappe.session.user)
    context.isFabricVendor = "Fabric Vendor" in context.roles
    
    return context
