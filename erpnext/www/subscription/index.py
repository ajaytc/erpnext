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
    if(context.brand.subscribed_plan):
        context.paymentPlan=frappe.get_doc("Payment Plan",context.brand.subscribed_plan)


    if ("Brand User" not in roles):
        frappe.throw(_("Not Permitted!"), frappe.PermissionError)

    brand = frappe.get_doc('User', frappe.session.user).brand_name
    context.plans = frappe.get_all("Payment Plan", fields=["plan_name", "name", "annual_price", "monthly_price", "trial_days",
                                                            "no_of_clients", "client", "supply", "pre_production", "shipment", "stock", "snf", "production"], order_by="annual_price")

    context.template=getPdfDoc(context)

    return context

def getPdfDoc(context):
    
    # params = frappe.form_dict
    # if('sk' in params):
    #     context.brand_name=context.supplier.brand
    # else:
    #     context.brand_name = frappe.get_doc('User', frappe.session.user).brand_name

    context.subscribedDate=context.brand.subscribed_date
    context.brandName=context.brand.company_name
    brand = frappe.get_all("User", filters={"type": "brand", "brand_name": context.brandName}, fields=[
        "user_image", "address1", "name","country"])
    context.brandAddress=brand[0].address1
    context.subscription_plan_name=context.paymentPlan.plan_name
    context.subscription_end_date=context.brand.subscription_end_date
    context.price=context.brand.amount
    context.totalPay=context.brand.fullpayment
    context.modules=[]

    mods=["client", "supply", "pre_production", "shipment", "stock", "snf", "production"]
    brandDict=context.brand.__dict__
    for mod in mods:
        module={
            'name':mod,
            'value':brandDict[mod]
        }
        context.modules.append(module)

    if(brand[0].country=='France'):
        context.vatRate=20
    else:
        context.vatRate=float(0)
    
    context.vatAmount=round(float(float(context.price)*(context.vatRate/100)),2)
    
    temp = frappe.get_all("Pdf Document", filters={"type": "Brand Subscription Invoice"}, fields=[
                          "content", "type", "name"])
    rendered_doc=frappe.render_template(temp[0]['content'],context)
    
    return rendered_doc