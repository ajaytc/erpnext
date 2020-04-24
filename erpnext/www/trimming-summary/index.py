from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime

no_cache = 1


def get_context(context):
    params = frappe.form_dict
    if('order' in params):
        context.trimOrder = frappe.get_doc('Trimming Order', params.order)
        context.trimmingItem=frappe.get_doc('Trimming Item',context.trimOrder.trimming_item);

    context.roles = frappe.get_roles(frappe.session.user)
    context.isTrimVendor = "Trimming Vendor" in context.roles
    return context