from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime

no_cache = 1


def get_context(context):
    brand = frappe.get_doc('User',frappe.session.user).brand_name;
    context.factories = frappe.get_list('Production Factory',filters={'brand': brand},fields=['city_town','name','country','factory_name','phone','email_address']);
    return context