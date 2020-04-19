from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime

no_cache = 1


def get_context(context):
    params = frappe.form_dict
    if('order' in params):
        context.order = frappe.get_doc('Production Order', params.order)

    context.roles = frappe.get_roles(frappe.session.user)
    context.isCustomer = "Customer" in context.roles
    context.isBrand = "Brand User" in context.roles

    # context.parents = [
    #     {"name": frappe._("Home"), "route": "/"}
    # ]
    
    return context
