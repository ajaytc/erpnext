from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list

no_cache = 1


def get_context(context):
    context.sizes = frappe.get_all("Sizing",fields=["size"])
    return context
