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
    context.destination = frappe.get_list("Production Factory")

    context.vendors = frappe.get_list("Supplier")

    query = """select t.internal_ref, t.item_category, t.color, s.quantity, s.localization, s.total_value, s.name, t.unit_price from `tabStock` s left join `tabTrimming Item` t on t.name = s.internal_ref where s.item_type=%s"""

    context.trimming = frappe.db.sql(query,"trimming")

    return context
