from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime
from frappe.utils.pdf import getBase64Img

no_cache = 1


def get_context(context):
    params = frappe.form_dict
    if('order' in params):
        context.trimOrder = frappe.get_doc('Trimming Order', params.order)
        context.trimmingItem = frappe.get_doc(
            'Trimming Item', context.trimOrder.trimming_item);
        context.supplier = frappe.get_doc(
            'Supplier', context.trimOrder.trimming_vendor)
        context.trimmingOrderShipment = frappe.get_all('Shipment Order', fields=[
                                                       'tracking_number', 'carrier_company', 'shipping_date', 'expected_delivery_date', 'shipping_price', 'html_tracking_link'], filters={'trimming_order_id': params.order})

    if frappe.session.user == 'Guest':
        context.isGuest=True
    else:
        context.isGuest=False
    context.roles = frappe.get_roles(frappe.session.user)
    context.isBrand = "Brand User" in context.roles


    

    if('sk' in params):
        context.isTrimVendor=True
    else:
        context.isTrimVendor = "Trimming Vendor" in context.roles

    # get data for pdf generation
    
    context.order_number=context.trimOrder.name
    context.creation=context.trimOrder.creation
    context.supplier_name=context.supplier.name
    context.supplier_address=context.supplier
    context.destination=getDestination(context) 
    if(context.trimmingItem.trimming_image != None):
        context.item_pic=context.trimmingItem.trimming_image
    else:
        context.item_pic=''
    context.item_ref=context.trimOrder.trimming_item
    context.color=context.trimmingItem.color
    context.size=context.trimmingItem.trimming_size
    context.order_type='Trimming'
    context.quantity=context.trimOrder.quantity
    context.template=getPdfDoc(context)
    return context


def getPdfDoc(context):

    # params = frappe.form_dict
    # if('sk' in params):
    #     context.brand_name=context.supplier.brand
    # else:
    #     context.brand_name = frappe.get_doc('User', frappe.session.user).brand_name

    context.brand_name=context.trimOrder.brand
    brand = frappe.get_all("User", filters={"type": "brand", "brand_name": context.brand_name}, fields=[
        "user_image", "address1", "name", "address2", "city", "zip_code", "country"])
    context.brand_logo=brand[0].user_image
    context.brandAddress=brand[0]
       
    path = 'erpnext/www/doc-templates/documents/supply-order-pdf.html'
    rendered_doc=frappe.render_template(path, context)
    
    return rendered_doc

def getDestination(context):
    dest=context.trimOrder.destination
    destination=frappe.get_doc("Production Factory",dest).factory_name

    return destination