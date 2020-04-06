from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list

no_cache = 1


def get_context(context):
    # context.orders = frappe.get_all(
        # "Sales Order", fields=["name", "creation", "docstatus"])

    context.orders = frappe.db.sql(
        """select so.name, so.creation, i.item_name, i.item_group from `tabSales Order` so left join `tabSales Order Item` i on i.parent = so.name""")

    return context
