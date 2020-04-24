from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime

no_cache = 1


def get_context(context):
    params = frappe.form_dict
    if('order' in params):
        context.packOrder = frappe.get_doc('Packaging Order', params.order)
        context.packItem=frappe.get_doc('Packaging Item',context.packOrder.packaging_item);

    context.roles = frappe.get_roles(frappe.session.user)
    context.isPackVendor = "Packaging Vendor" in context.roles
    return context