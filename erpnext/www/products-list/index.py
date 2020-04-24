from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime

no_cache = 1


def get_context(context):
    
    brand = frappe.get_doc('User',frappe.session.user).brand_name;
    context.items = frappe.get_list('Item', filters={'brand': brand}, fields=['item_group','item_name','name']);
    return context
