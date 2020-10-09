from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime
from erpnext.modehero.user import haveAccess

def get_context(context):
    if frappe.session.user == 'Guest':
        frappe.throw(
            _("You need to be logged in to access this page"), frappe.PermissionError)

    module = 'production'
    if(not haveAccess(module)):
        frappe.throw(
            _("You have not subscribed to this service"), frappe.PermissionError)
            
    roles = frappe.get_roles(frappe.session.user)

    if ("Administrator" not in roles) and ("Brand User" not in roles):
        frappe.throw(_("Not Permitted!"), frappe.PermissionError)
    
    brand = frappe.get_doc('User', frappe.session.user).brand_name

    # pricing_details = frappe.get_all('Client Pricing', filters={'brand': brand}, fields=['client','item_group','item_code'])

    context.clients=frappe.db.sql("""select distinct client from `tabClient Pricing` where brand=%s""",brand)

    return context

