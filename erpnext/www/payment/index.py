import frappe
import json
import ast
import datetime
from frappe import _

def get_context(context):
    if frappe.session.user == 'Guest':
        frappe.throw(
            _("You need to be logged in to access this page"), frappe.PermissionError)
    roles = frappe.get_roles(frappe.session.user)

    if ("Brand User" not in roles):
        frappe.throw(_("Not Permitted!"), frappe.PermissionError)

    context.trialdays=context.trial_period=frappe.get_all('System Data',filters={'type':'brand-trial-period'},fields=['value'])[0].value

    brand = frappe.get_doc('User', frappe.session.user)
    params = frappe.form_dict
    context.plan=frappe.get_doc('Payment Plan', params.name)
    context.plan_period=params.period
    if(brand.country=='France'):
        context.vatRate=20
        context.vat_rate='20%'
    else:
        context.vatRate=0
        context.vat_rate='0%'

    context.fullPayment=getFullPayment(context)
    # context.plans=frappe.get_list("Payment Plan",fields=["plan_name","name","annual_price","monthly_price","trial_days","no_of_clients","client","supply","pre_production","shipment","stock","snf","production"],order_by="annual_price")
    
    return context

def getFullPayment(context):
    if(context.plan_period=='Monthly'):
        price=context.plan.monthly_price
    elif(context.plan_period=='Annually'):
        price=context.plan.annual_price
    vatAmount=float(float(price)*float(context.vatRate/100))
    fullPayment=float(price)+vatAmount

    return fullPayment

