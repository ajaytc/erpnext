from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list

no_cache = 1


def get_context(context):
    context.username = frappe.get_doc('User', frappe.session.user).full_name
    return context
