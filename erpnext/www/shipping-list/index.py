# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list

no_cache = 1


def get_context(context):
    if frappe.session.user == 'Guest':
        frappe.throw(
            _("You need to be logged in to access this page"), frappe.PermissionError)

    context.show_sidebar = False
    context.status = 'active'

    query = """select so.internal_ref, i.item_name, so.shipping_date, so.expected_delivery_date, i.item_destination from `tabShipment Order` so left join `tabSales Order Item` i on i.name = so.product_order_id"""
    context.active = frappe.db.sql(query+" where i.docstatus=1")
    context.completed = frappe.db.sql(query+" where i.docstatus=0")
    
    # context.parents = [
    #     {"name": frappe._("Home"), "route": "/"}
    # ]

    return context
