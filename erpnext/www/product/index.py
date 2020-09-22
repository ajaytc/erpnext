from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime
from frappe.utils.pdf import getBase64Img
no_cache = 1


def get_context(context):
    params = frappe.form_dict
    if('name' in params):
        context.product = frappe.get_doc('Item', params.name)
        # context.packItem=frappe.get_doc('Packaging Item',context.packOrder.packaging_item);
        # context.supplier=frappe.get_doc('Supplier',context.packOrder.packaging_vendor)
        # context.packagingOrderShipment=frappe.get_all('Shipment Order',fields=['tracking_number','carrier_company','shipping_date','expected_delivery_date','shipping_price','html_tracking_link'],filters={'packaging_order_id':params.order})
    
    context.roles = frappe.get_roles(frappe.session.user)
    context.isBrand = "Brand User" in context.roles
    context.brand=frappe.get_doc('User', frappe.session.user).brand_name

    suppliersDic={}
    for supplier in context.product.supplier:
        if supplier.supplier_group  not in suppliersDic:
            suppliersDic[supplier.supplier_group]=[]
        suppliersDic[supplier.supplier_group].append(supplier)

    context.suppliers=suppliersDic

            

    
    
    
    return context


