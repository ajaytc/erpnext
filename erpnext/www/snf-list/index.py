from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime


def get_context(context):
    if frappe.session.user == 'Guest':
        frappe.throw(
            _("You need to be logged in to access this page"), frappe.PermissionError)
    roles = frappe.get_roles(frappe.session.user)
    if ("Administrator" not in roles):
        frappe.throw(_("Not Permitted!"), frappe.PermissionError)
    supplier_list = frappe.get_all("Supplier",["name","creation","is_official","supplier_group","brand","subscribed_date","subscription_end_date","enabled"])
    factory_list = frappe.get_all("Production Factory",["name","creation","factory_name","is_official","brand","subscribed_date","subscription_end_date","enabled"])
    global_list = supplier_list + factory_list
    context.global_list = sorted(global_list, key=lambda k: k['creation']) 

    return context
