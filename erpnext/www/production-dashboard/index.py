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

    context.preprod_onprocess = frappe.get_list(
        'Production Order', filters={'docstatus': 0}, fields=['name', 'internal_ref', 'product_name', 'product_category', 'creation', 'expected_work_date'])
    context.preprod_finished = frappe.get_list(
        'Production Order', filters={'docstatus': 1}, fields=['name', 'internal_ref', 'product_name', 'product_category', 'creation', 'tracking_number', 'expected_work_date'])
    context.prod_onprocess = frappe.get_list(
        'Production Order', filters={'docstatus': 2}, fields=['name', 'internal_ref', 'product_name', 'product_category', 'creation', 'expected_work_date'])
    context.prod_finished = frappe.get_list(
        'Production Order', filters={'docstatus': 3}, fields=['name', 'internal_ref', 'product_name', 'product_category', 'creation', 'tracking_number', 'expected_work_date'])

    return context
