# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
from erpnext.modehero.user import haveAccess

no_cache = 1


def get_context(context):
    module='supply'
    if frappe.session.user == 'Guest':
        frappe.throw(
            _("You need to be logged in to access this page"), frappe.PermissionError)
    
    

    context.roles = frappe.get_roles(frappe.session.user)

    params = frappe.form_dict
    if('type' in params):
        context.isSupplier=False
        if params.type == 'fabric':
            context.isFabric = True
        elif params.type == 'trimming':
            context.isTrimming = True
        elif params.type == 'packaging':
            context.isPackaging = True

    else:
        context.isSupplier=True
        context.isFabric = "Fabric Vendor" in context.roles
        context.isPackaging = "Packaging Vendor" in context.roles
        context.isTrimming = "Trimming Vendor" in context.roles

    fields = ['internal_ref', 'name', 'product_name', 'brand', 'creation',
              'tracking_number', 'ex_work_date', 'profoma', 'shipment_date', 'invoice', 'destination']
    fabric_fields = fields+['fabric_ref as item_ref']
    trimming_fields = fields+['trimming_item as item_ref']
    packaging_fields = fields+['packaging_item as item_ref']

    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name

    # if brand access the dashboard
    if(context.isSupplier==False):
        if(not haveAccess(module)):
            frappe.throw(
            _("You have not subscribed to this service"), frappe.PermissionError)
        if context.isFabric:
            context.orderType = 'Fabric Order'
            context.neworders = frappe.get_all(
                context.orderType, filters={'docstatus': 0, 'brand': brand}, fields=fabric_fields)
            context.onprocess = frappe.get_all(
                context.orderType, filters={'docstatus': 1, 'brand': brand}, fields=fabric_fields)
            context.ready = frappe.get_all(
                context.orderType, filters={'docstatus': 4, 'brand': brand}, fields=fabric_fields)
            context.shipped = frappe.get_all(
                context.orderType, filters={'docstatus': 3, 'brand': brand}, fields=fabric_fields)
            context.canceled = frappe.get_all(
                context.orderType, filters={'docstatus': 2, 'brand': brand}, fields=fabric_fields)

        elif context.isPackaging:
            context.orderType = 'Packaging Order'
            context.neworders = frappe.get_all(
                context.orderType, filters={'docstatus': 0, 'brand': brand}, fields=packaging_fields)
            context.onprocess = frappe.get_all(
                context.orderType, filters={'docstatus': 1, 'brand': brand}, fields=packaging_fields)
            context.ready = frappe.get_all(
                context.orderType, filters={'docstatus': 4, 'brand': brand}, fields=packaging_fields)
            context.shipped = frappe.get_all(
                context.orderType, filters={'docstatus': 3, 'brand': brand}, fields=packaging_fields)
            context.canceled = frappe.get_all(
                context.orderType, filters={'docstatus': 2, 'brand': brand}, fields=packaging_fields)

        elif context.isTrimming:
            context.orderType = 'Trimming Order'
            context.neworders = frappe.get_all(
                context.orderType, filters={'docstatus': 0, 'brand': brand}, fields=trimming_fields)
            context.onprocess = frappe.get_all(
                context.orderType, filters={'docstatus': 1, 'brand': brand}, fields=trimming_fields)
            context.ready = frappe.get_all(
                context.orderType, filters={'docstatus': 4, 'brand': brand}, fields=trimming_fields)
            context.shipped = frappe.get_all(
                context.orderType, filters={'docstatus': 3, 'brand': brand}, fields=trimming_fields)
            context.canceled = frappe.get_all(
                context.orderType, filters={'docstatus': 2, 'brand': brand}, fields=trimming_fields)

    else:
        # if supplier access the dashboard
        vendor_name=frappe.get_all('Supplier',filters={'email':user.name},fields=['name'])
        if context.isFabric:
            context.orderType = 'Fabric Order'
            context.neworders = frappe.get_all(
                context.orderType, filters={'docstatus': 0, 'fabric_vendor': vendor_name[0]['name']}, fields=fabric_fields)
            context.onprocess = frappe.get_all(
                context.orderType, filters={'docstatus': 1, 'fabric_vendor': vendor_name[0]['name']}, fields=fabric_fields)
            context.ready = frappe.get_all(
                context.orderType, filters={'docstatus': 4, 'fabric_vendor': vendor_name[0]['name']}, fields=fabric_fields)
            context.shipped = frappe.get_all(
                context.orderType, filters={'docstatus': 3, 'fabric_vendor': vendor_name[0]['name']}, fields=fabric_fields)
            context.canceled = frappe.get_all(
                context.orderType, filters={'docstatus': 2, 'fabric_vendor': vendor_name[0]['name']}, fields=fabric_fields)

        elif context.isPackaging:
            context.orderType = 'Packaging Order'
            context.neworders = frappe.get_all(
                context.orderType, filters={'docstatus': 0, 'packaging_vendor': vendor_name[0]['name']}, fields=packaging_fields)
            context.onprocess = frappe.get_all(
                context.orderType, filters={'docstatus': 1, 'packaging_vendor': vendor_name[0]['name']}, fields=packaging_fields)
            context.ready = frappe.get_all(
                context.orderType, filters={'docstatus': 4, 'packaging_vendor': vendor_name[0]['name']}, fields=packaging_fields)
            context.shipped = frappe.get_all(
                context.orderType, filters={'docstatus': 3, 'packaging_vendor': vendor_name[0]['name']}, fields=packaging_fields)
            context.canceled = frappe.get_all(
                context.orderType, filters={'docstatus': 2, 'packaging_vendor': vendor_name[0]['name']}, fields=packaging_fields)


        elif context.isTrimming:
            context.orderType = 'Trimming Order'
            context.neworders = frappe.get_all(
                context.orderType, filters={'docstatus': 0, 'trimming_vendor': vendor_name[0]['name']}, fields=trimming_fields)
            context.onprocess = frappe.get_all(
                context.orderType, filters={'docstatus': 1, 'trimming_vendor': vendor_name[0]['name']}, fields=trimming_fields)
            context.ready = frappe.get_all(
                context.orderType, filters={'docstatus': 4, 'trimming_vendor': vendor_name[0]['name']}, fields=trimming_fields)
            context.shipped = frappe.get_all(
                context.orderType, filters={'docstatus': 3, 'trimming_vendor': vendor_name[0]['name']}, fields=trimming_fields)
            context.canceled = frappe.get_all(
                context.orderType, filters={'docstatus': 2, 'trimming_vendor': vendor_name[0]['name']}, fields=trimming_fields)
    

    # context.parents = [
    #     {"name": frappe._("Home"), "route": "/"}
    # ]

    return context
