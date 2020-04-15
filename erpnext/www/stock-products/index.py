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

    brand = frappe.get_doc("User", frappe.session.user).brand_name

    query = """select i.item_name, s.quantity, s.localization, s.total_value from `tabStock` s left join `tabItem` i on i.item_code = s.product where s.item_type=%s and i.brand=%s"""

    context.products = frappe.db.sql(query,("product",brand))

    return context
