from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list

no_cache = 1


def get_context(context):
    context.sizes = frappe.get_list("Sizing", fields=["size"])
    context.products = frappe.get_list("Item")

    context.garmentlabel = frappe.get_list("Garment Label")

    context.roles = frappe.get_roles(frappe.session.user)
    context.isCustomer = "Customer" in context.roles
    context.isBrand = "Brand User" in context.roles
    return context
