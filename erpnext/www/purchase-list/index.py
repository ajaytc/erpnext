from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime

no_cache = 1


def get_context(context):

    # brand = frappe.get_doc('User', frappe.session.user).brand_name
    # context.orders = frappe.get_list('Sales Order', filters={'company': brand, 'docstatus': 0}, fields=[
    #     'name', 'customer'])
    return context
