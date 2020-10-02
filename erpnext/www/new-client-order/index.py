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
        context.products = frappe.get_all(
            "Item", filters={'brand': brand}, fields=['name', 'item_name'])

        context.garmentlabel = frappe.get_list("Garment Label")

        client = frappe.get_all("Customer", filters={
                                 "user": frappe.session.user})
        # if(True or len(client) == 0):
        # frappe.throw("No customers for user")

        if(len(client) > 0):
            context.destinations = frappe.get_all(
                "Destination", filters={"client_name": client[0].name})
        else:
            context.destinations = []

        context.date = datetime.date.today()

    else:
        context.order = frappe.get_doc('Sales Order', params.order)
        context.qtys = {}
        for i in context.order.items:
            if i.free_size_qty!=None and i.first_free_size_qty!=None:
                context.free_size_product = True
                context.qtys[i.name] = [{"size":"Free Size","modified_quantity":i.free_size_qty,"quantity":i.first_free_size_qty}]
            else:
                context.qtys[i.name] = frappe.get_all(
                    'Quantity Per Size', filters={'order_id': i.name}, order_by='creation asc')

    context.roles = frappe.get_roles(frappe.session.user)
    context.isCustomer = "Customer" in context.roles
    context.isBrand = "Brand User" in context.roles
    return context
