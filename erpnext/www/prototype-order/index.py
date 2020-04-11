from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime

no_cache = 1


def get_context(context):
    params = frappe.form_dict
    if('order' not in params):
        # context.sizes = frappe.get_list(
        #     "Sizing", fields=["size"], order_by='idx')
        brand = frappe.get_doc("User", frappe.session.user).brand_name
        context.products = frappe.get_list("Item", filters={'brand': brand})

        context.garmentlabel = frappe.get_list("Garment Label")

        client = frappe.get_list("Customer", filters={
                                 "user": frappe.session.user})
        # if(True or len(client) == 0):
        # frappe.throw("No customers for user")

        if(len(client) > 0):
            context.destinations = frappe.get_list(
                "Destination", filters={"client_name": client[0].name})
        else:
            context.destinations = []

        context.date = datetime.date.today()

    else:
        context.order = frappe.get_doc('Sales Order', params.order)
        context.qtys = {}
        for i in context.order.items:
            context.qtys[i.name] = frappe.get_list(
                'Quantity Per Size', filters={'order_id': i.name})

    context.roles = frappe.get_roles(frappe.session.user)
    context.isCustomer = "Customer" in context.roles
    context.isBrand = "Brand User" in context.roles
    return context
