import frappe.www.list
import datetime
from frappe import _
from erpnext.modehero.user import haveAccess
no_cache = 1


def get_context(context):
    module = 'production'
    if(not haveAccess(module)):
        frappe.throw(_("You have not subscribed to this service"),
                     frappe.PermissionError)
    context.brand = frappe.get_doc("User", frappe.session.user).brand_name

    # context.parents = [
    #     {"name": frappe._("Home"), "route": "/"},
    # ]

    return context
