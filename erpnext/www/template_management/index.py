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

    if ("Administrator" not in roles) and ("Brand User" not in roles):
        frappe.throw(_("Not Permitted!"), frappe.PermissionError)

    #get url parameters
    params = frappe.form_dict
    if('type' in params):
        context.type=params.type
    
    if('case' in params):
        context.case=params.case

    
    #business logic 
    if(context.case=='pdf'):
        temp=frappe.get_all("Pdf Document",fields=["content","type","name"])
        context.pdf_template_names=temp
    elif (context.case=='email'):
        temp=frappe.get_all("Notification")
        context.email_template_names=temp[0:1]
        # context.subject=temp.subject
    
    

    return context