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

    query = """select so.name, i.creation, i.item_name, i.item_group, i.item_destination, so.internal_ref, so.profoma from `tabSales Order` so left join `tabSales Order Item` i on i.parent = so.name"""
    context.waiting = frappe.db.sql(
        query+" where i.docstatus=0 order by so.creation desc")
    context.onprocess = frappe.db.sql(
        query+" where i.docstatus=1  order by so.creation desc")
    context.shipped = frappe.db.sql(
        query+" where i.docstatus=3  order by so.creation desc")
    context.cancelled = frappe.db.sql(
        query+" where i.docstatus=2  order by so.creation desc")

    # context.parents = [
    #     {"name": frappe._("Home"), "route": "/"}
    # ]
    context.roles = frappe.get_roles(frappe.session.user)
    context.isCustomer = "Customer" in context.roles
    context.isBrand = "Brand User" in context.roles

    if context.isCustomer:
        customer = frappe.get_list(
            'Customer', filters={'user': frappe.session.user})[0].name
        context.destinations = frappe.get_all(
            "Destination", filters={'client_name': customer}, fields=["destination_name", "city_town", "client_name", "name"])

    context = frappe._dict({
        "post_login": [
            {"label": _("Account"), "url": "/update-profile"},
            {"label": _("Destination"), "url": "/client-destinations"},
            {"label": _("Logout"), "url": "/?cmd=web_logout"}
        ]
    })

    return context
