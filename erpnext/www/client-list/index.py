from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime
from erpnext.modehero.user import haveAccess

no_cache = 1


def get_context(context):
    module = 'client'
    if(not haveAccess(module)):
        frappe.throw(
            _("You have not subscribed to this service"), frappe.PermissionError)
    brand = frappe.get_doc('User', frappe.session.user).brand_name
    context.customers = frappe.get_all('Customer', fields=[
                                       'city', 'zip_code', 'country', 'name', 'customer_name', 'contact', 'phone', 'email_address'], filters={'brand': brand})
    return context
