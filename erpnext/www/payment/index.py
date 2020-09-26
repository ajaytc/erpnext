import frappe
import json
import ast
import datetime

def get_context(context):
    if frappe.session.user == 'Guest':
        frappe.throw(
            _("You need to be logged in to access this page"), frappe.PermissionError)
    roles = frappe.get_roles(frappe.session.user)

    if ("Brand User" not in roles):
        frappe.throw(_("Not Permitted!"), frappe.PermissionError)

    brand = frappe.get_doc('User', frappe.session.user).brand_name
    params = frappe.form_dict
    context.plan=frappe.get_doc('Payment Plan', params.name)
    context.plan_period=params.period
    # context.plans=frappe.get_list("Payment Plan",fields=["plan_name","name","annual_price","monthly_price","trial_days","no_of_clients","client","supply","pre_production","shipment","stock","snf","production"],order_by="annual_price")
    
    return context

