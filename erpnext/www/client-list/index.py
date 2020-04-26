from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime

no_cache = 1


def get_context(context):    
    # brand = frappe.get_doc('User',frappe.session.user).brand_name;
    context.customers = frappe.get_list('Customer',fields=['city','zip_code','country','name','customer_name','contact','phone','email_address']);
    return context