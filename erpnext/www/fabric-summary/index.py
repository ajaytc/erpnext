from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime
from frappe.utils.pdf import getBase64Img

no_cache = 1


def get_context(context):
    # if frappe.session.user == 'Guest':
    #     frappe.throw(
    #         _("You need to be logged in to access this page"), frappe.PermissionError)     
    params = frappe.form_dict
    if('order' in params):
        context.fabricOrder = frappe.get_doc('Fabric Order', params.order)
        context.fabric=frappe.get_doc('Fabric',context.fabricOrder.fabric_ref);
        context.supplier=frappe.get_doc('Supplier',context.fabricOrder.fabric_vendor)
        context.fabricOrderShipment=frappe.get_all('Shipment Order',fields=['tracking_number','carrier_company','shipping_date','expected_delivery_date','shipping_price','html_tracking_link'],filters={'fabric_order_id':params.order})
    
    if frappe.session.user == 'Guest':
        context.isGuest=True
    else:
        context.isGuest=False
        
    context.roles = frappe.get_roles(frappe.session.user)
    context.isBrand = "Brand User" in context.roles

    if('sk' in params):
        context.isFabricVendor=True
    else:
        context.isFabricVendor = "Fabric Vendor" in context.roles
    

    # get data for pdf generation
    
    context.order_number=context.fabricOrder.internal_ref
    context.creation=context.fabricOrder.creation
    context.supplier_name=context.supplier.name
    context.supplier_address=context.supplier.address1
    context.destination=context.fabricOrder.destination
    if(context.fabric.fabric_image != None):
        context.item_pic=getBase64Img(context.fabric.fabric_image)
    else:
        context.item_pic=''
    context.item_ref=context.fabricOrder.fabric_ref
    context.color=context.fabric.color
    context.size=None
    context.order_type='Fabric'
    context.quantity=context.fabricOrder.quantity
    context.template=getPdfDoc(context)


    
    
    
    return context

def getPdfDoc(context):

    # params = frappe.form_dict
    # if('sk' in params):
    #     context.brand_name=context.supplier.brand
    # else:
    #     context.brand_name = frappe.get_doc('User', frappe.session.user).brand_name

    context.brand_name=context.fabricOrder.brand
    brand = frappe.get_all("User", filters={"type": "brand", "brand_name": context.brand_name}, fields=[
        "user_image", "address1", "name"])
    context.brand_logo=getBase64Img(brand[0].user_image)
    context.address=brand[0].address1
    temp = frappe.get_all("Pdf Document", filters={"type": "Supply Order"}, fields=[
                          "content", "type", "name"])
    rendered_doc=frappe.render_template(temp[0]['content'],context)
    
    return rendered_doc
    

    
