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
    context.status = 'waiting'

    context.onprocess = frappe.get_list(
        'Prototype Order', filters={'docstatus': 0}, fields=['name', 'internal_ref', 'product', 'product_category', 'quantity_per_size', 'creation', 'ex_work_date', 'tracking_number'])
    context.validate = frappe.get_list(
        'Prototype Order', filters={'docstatus': 1}, fields=['name', 'internal_ref', 'product', 'product_category', 'quantity_per_size', 'creation', 'tracking_number'])
    context.notvalidate = frappe.get_list(
        'Prototype Order', filters={'docstatus': 2}, fields=['name', 'internal_ref', 'product', 'product_category'])

    # context.parents = [
    #     {"name": frappe._("Home"), "route": "/"}
    # ]

    return context
