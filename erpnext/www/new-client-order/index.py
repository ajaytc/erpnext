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
        user =  frappe.session.user
        brand = frappe.get_doc("User",user).brand_name
        client = frappe.get_all("Customer",{"user":user},["name","package_only","brand"])
        if len(client)>0:
            context.products = get_products_of_client(client[0])
            context.destinations = frappe.get_all(
                "Destination", filters={"client_name": client[0]["name"]})
        else:
            context.products = []
            context.destinations = []
        context.garmentlabel = frappe.get_list("Garment Label")

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

def get_products_of_client(client_doc):
    products = []
    if client_doc["package_only"]:
        package_items = frappe.get_all("Package",{"brand":client_doc["brand"],"client":client_doc["name"]},["item_code"])
        for item in package_items:
            item = frappe.get_all("Item",{"name":item["item_code"]},["name","item_name"])
            if len(item)>0:
                products.append(item[0])
    else:
        products = frappe.get_all("Item", filters={'brand': client_doc["brand"]}, fields=['name', 'item_name'])
    return products