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
        context.packOrder = frappe.get_doc('Packaging Order', params.order)
        context.packItem=frappe.get_doc('Packaging Item',context.packOrder.packaging_item);
        supplier=frappe.get_doc('Supplier',context.packOrder.packaging_vendor)
        context.packagingOrderShipment=frappe.get_all('Shipment Order',fields=['tracking_number','carrier_company','shipping_date','expected_delivery_date','shipping_price','html_tracking_link'],filters={'packaging_order_id':params.order})
    

    context.roles = frappe.get_roles(frappe.session.user)
    context.isPackVendor = "Packaging Vendor" in context.roles

    # get data for pdf generation
    
    context.order_number=context.packOrder.internal_ref
    context.creation=context.packOrder.creation
    context.supplier_name=supplier.name
    context.supplier_address=supplier.address1
    context.destination=context.packOrder.destination
    if(context.packItem.packaging_image != None):
        context.item_pic=getBase64Img(context.packItem.packaging_image )
    else:
        context.item_pic=''
    context.item_ref=context.packOrder.packaging_item
    context.color=context.packItem.color
    context.size=context.packItem.packaging_size
    context.order_type='Packaging'
    context.quantity=context.packOrder.quantity
    context.template=getPdfDoc(context)
    return context


def getPdfDoc(context):
    brand_name = frappe.get_doc('User', frappe.session.user).brand_name

    brand = frappe.get_all("User", filters={"type": "brand", "brand_name": brand_name}, fields=[
        "user_image", "address1", "name"])
    context.brand_logo=getBase64Img(brand[0].user_image)
    context.address=brand[0].address1
    temp = frappe.get_all("Pdf Document", filters={"type": "Supply Order"}, fields=[
                          "content", "type", "name"])
    rendered_doc=frappe.render_template(temp[0]['content'],context)
    
    return rendered_doc