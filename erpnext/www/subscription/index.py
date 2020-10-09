from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime



def get_context(context):
    #check user roles
    if frappe.session.user == 'Guest':
        frappe.throw(
            _("You need to be logged in to access this page"), frappe.PermissionError)
    roles = frappe.get_roles(frappe.session.user)

    brandName=frappe.get_doc('User', frappe.session.user).brand_name
    context.brand=frappe.get_doc("Company",brandName)
    context.paymentPlan=frappe.get_doc("Payment Plan",context.brand.subscribed_plan)


    if ("Brand User" not in roles):
        frappe.throw(_("Not Permitted!"), frappe.PermissionError)

    brand = frappe.get_doc('User', frappe.session.user).brand_name
    context.plans = frappe.get_all("Payment Plan", fields=["plan_name", "name", "annual_price", "monthly_price", "trial_days",
                                                            "no_of_clients", "client", "supply", "pre_production", "shipment", "stock", "snf", "production"], order_by="annual_price")

    return context
