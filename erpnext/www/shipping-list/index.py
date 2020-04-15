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

    brand = frappe.get_doc("User", frappe.session.user).brand_name

    query = """select so.internal_ref, i.item_name, so.shipping_date, so.expected_delivery_date, i.item_destination 
                from `tabSales Order Item` i
                left join `tabShipment Order` so on i.name = so.product_order_id
                right join `tabSales Order` s on s.name = i.parent
                where i.docstatus=%s and s.company=%s"""
    context.active = frappe.db.sql(query,(1,brand))
    context.completed = frappe.db.sql(query,(0,brand))
    
    # context.parents = [
    #     {"name": frappe._("Home"), "route": "/"}
    # ]

    return context
