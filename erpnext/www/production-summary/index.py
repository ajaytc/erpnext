from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime

no_cache = 1




def get_context(context):
    fabSuppliers = []
    trimSuppliers = []
    packSuppliers = []
    params = frappe.form_dict
    if('order' in params):
        context.order = frappe.get_doc('Production Order', params.order)

    context.product = frappe.get_doc('Item', context.order.product_name)

    getFabricSuppliers(context.order,fabSuppliers,trimSuppliers,packSuppliers)

    context.fabricSuppliers = fabSuppliers
    context.trimmingSuppliers = trimSuppliers
    context.packagingSuppliers = packSuppliers

    context.roles = frappe.get_roles(frappe.session.user)
    context.isCustomer = "Customer" in context.roles
    context.isBrand = "Brand User" in context.roles
    context.isProd = "Manufacturing User" in context.roles

    # context.parents = [
    #     {"name": frappe._("Home"), "route": "/"}
    # ]

    return context


def getFabricSuppliers(order,fabSuppliers,trimSuppliers,packSuppliers):
    suppliers = order.suppliers

    for supplier in suppliers:
        if(supplier.supplier_group == 'Fabric'):
            fabSuppliers.append(supplier)
        elif (supplier.supplier_group == 'Trimming'):
            trimSuppliers.append(supplier)
        elif (supplier.supplier_group == 'Packaging'):
            packSuppliers.append(supplier)
