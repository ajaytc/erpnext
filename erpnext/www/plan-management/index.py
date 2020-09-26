import frappe
import json
import ast
import datetime

def get_context(context):
    if frappe.session.user == 'Guest':
        frappe.throw(
            _("You need to be logged in to access this page"), frappe.PermissionError)
    roles = frappe.get_roles(frappe.session.user)

    if ("Administrator" not in roles):
        frappe.throw(_("Not Permitted!"), frappe.PermissionError)

    brand = frappe.get_doc('User', frappe.session.user).brand_name
    context.trial_period=frappe.get_all('System Data',filters={'type':'brand-trial-period'},fields=['value'])[0].value
    # trial_period_array=frappe.get_all('System Data',filters={'type':'brand-trial-period'})
    # trial_periodOb=frappe.get_doc('System Data',trial_period_array[0].name)
    context.plans=frappe.get_list("Payment Plan",fields=["plan_name","name","annual_price","monthly_price","trial_days","no_of_clients","client","supply","pre_production","shipment","stock","snf","production"],order_by="annual_price")
    
    return context


