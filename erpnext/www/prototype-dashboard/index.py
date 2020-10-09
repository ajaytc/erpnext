# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
from erpnext.modehero.user import haveAccess
no_cache = 1


def get_context(context):
    # if frappe.session.user == 'Guest':
    #     frappe.throw(
    #         _("You need to be logged in to access this page"), frappe.PermissionError)
    module = 'pre_production'
    if(not haveAccess(module)):
        frappe.throw(
            _("You have not subscribed to this service"), frappe.PermissionError)

    context.show_sidebar = False
    brand = frappe.get_doc("User", frappe.session.user).brand_name

    context.onprocess = frappe.get_all(
        'Prototype Order', filters={'docstatus': 0, 'brand': brand}, fields=['name', 'internal_ref', 'product', 'product_category', 'quantity_per_size', 'creation', 'ex_work_date', 'tracking_number'])
    context.validate = frappe.get_all(
        'Prototype Order', filters={'docstatus': 1, 'brand': brand}, fields=['name', 'internal_ref', 'product', 'product_category', 'quantity_per_size', 'creation', 'tracking_number'])
    context.notvalidate = frappe.get_all(
        'Prototype Order', filters={'docstatus': 2, 'brand': brand}, fields=['name', 'internal_ref', 'product', 'product_category'])

    # context.parents = [
    #     {"name": frappe._("Home"), "route": "/"}
    # ]

    return context
