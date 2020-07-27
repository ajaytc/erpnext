from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime



def get_context(context):
    
    temp=frappe.get_all("Pdf Document",filters={"type":"Bulk Order"},fields=["content","type","name"])
    
    context.template=temp[0]['content']

    return context