# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
from erpnext.modehero.user import haveAccess
from erpnext.modehero.product import get_product_cat_names
no_cache = 1


def get_context(context):
    # if frappe.session.user == 'Guest':
    #     frappe.throw(
    #         _("You need to be logged in to access this page"), frappe.PermissionError)
    module = 'pre_production'
    context.roles = frappe.get_roles(frappe.session.user)
    context.isBrand = "Brand User" in context.roles
    context.isManufacture = "Manufacturing User" in context.roles
    if(context.isBrand):
        if(not haveAccess(module)):
            frappe.throw(
                _("You have not subscribed to this service"), frappe.PermissionError)
    elif (context.isManufacture):
        if(not haveAccessForFactory(module)):
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
    context.support_dic_product_cats = get_product_cat_names(context.onprocess+context.validate+context.notvalidate,brand)
    return context
