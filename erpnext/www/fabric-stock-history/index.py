from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime

no_cache = 1


def get_context(context):
    params = frappe.form_dict
    if('stock' in params):
        context.stock = frappe.get_doc('Stock', params.stock)

    context.product = frappe.get_doc("Fabric", context.stock.internal_ref)

    context.historyList = frappe.get_all("Stock History", fields=[
                                         "in_out,name,creation,quantity"], filters={"parent": context.stock.name})

    return context
