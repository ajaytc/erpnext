import frappe.www.list
import datetime

no_cache = 1


def get_context(context):
    context.brand = frappe.get_doc("User", frappe.session.user).brand_name

    

    # context.parents = [
    #     {"name": frappe._("Home"), "route": "/"},
    # ]

    return context