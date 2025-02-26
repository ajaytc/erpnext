from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime
from erpnext.modehero.user import haveAccess
no_cache = 1


def get_context(context):
    module = 'pre_production'
    if(not haveAccess(module)):
        frappe.throw(
            _("You have not subscribed to this service"), frappe.PermissionError)
    params = frappe.form_dict
    # context.sizes = frappe.get_list(
    #     "Sizing", fields=["size"], order_by='idx')
    brand = frappe.get_doc("User", frappe.session.user).brand_name
    context.products = frappe.get_list(
        "Item", filters={'brand': brand}, fields=['name', 'item_name'])

    context.garmentlabel = frappe.get_list("Garment Label")

    client = frappe.get_list("Customer", filters={
        "user": frappe.session.user})
    # if(True or len(client) == 0):
    # frappe.throw("No customers for user")

    # if(len(client) > 0):
    #     context.destinations = frappe.get_list(
    #         "Destination", filters={"client_name": client[0].name})
    # else:
    #     context.destinations = []
    dests=frappe.get_all('Destination',filters={'brand':brand})
    pos= frappe.get_all('Point Of Sales',filters={'brand':brand},fields=['name','point_of_sale'])
    context.destinations=[]
    context.destinations.extend(dests)
    context.destinations.extend(pos)
    
   

    context.categories = frappe.get_list(
        'Item Group', filters={'brand_name': brand},fields=["name","item_group_name"])

    context.roles = frappe.get_roles(frappe.session.user)
    context.isCustomer = "Customer" in context.roles
    context.isBrand = "Brand User" in context.roles
    return context
