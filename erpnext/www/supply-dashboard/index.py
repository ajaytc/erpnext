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

    context.roles = frappe.get_roles(frappe.session.user)

    params = frappe.form_dict
    if('type' in params):
        if params.type == 'fabric':
            context.isFabric = True
        elif params.type == 'trimming':
            context.isTrimming = True
        elif params.type == 'packaging':
            context.isPackaging = True
    else:
        context.isFabric = "Fabric Vendor" in context.roles
        context.isPackaging = "Packaging Vendor" in context.roles
        context.isTrimming = "Trimming Vendor" in context.roles

    fileds = ['internal_ref', 'name', 'product_name', 'brand_name', 'creation',
              'tracking_number', 'ex_work_date', 'profoma', 'shipment_date', 'invoice']

    if context.isFabric:
        orderType = 'Fabric Order'
        context.neworders = frappe.get_all(
            orderType, filters={'docstatus': 0}, fields=fileds)
        context.onprocess = frappe.get_all(
            orderType, filters={'docstatus': 1}, fields=fileds)
        context.ready = frappe.get_all(
            orderType, filters={'docstatus': 2}, fields=fileds)
        context.shipped = frappe.get_all(
            orderType, filters={'docstatus': 3}, fields=fileds)

    elif context.isPackaging:
        orderType = 'Packaging Order'
        context.neworders = frappe.get_all(
            orderType, filters={'docstatus': 0}, fields=fileds)
        context.onprocess = frappe.get_all(
            orderType, filters={'docstatus': 1}, fields=fileds)
        context.ready = frappe.get_all(
            orderType, filters={'docstatus': 2}, fields=fileds)
        context.shipped = frappe.get_all(
            orderType, filters={'docstatus': 3}, fields=fileds)

    elif context.isTrimming:
        orderType = 'Trimming Order'
        context.neworders = frappe.get_all(
            orderType, filters={'docstatus': 0}, fields=fileds)
        context.onprocess = frappe.get_all(
            orderType, filters={'docstatus': 1}, fields=fileds)
        context.ready = frappe.get_all(
            orderType, filters={'docstatus': 2}, fields=fileds)
        context.shipped = frappe.get_all(
            orderType, filters={'docstatus': 3}, fields=fileds)

    # context.parents = [
    #     {"name": frappe._("Home"), "route": "/"}
    # ]

    return context
