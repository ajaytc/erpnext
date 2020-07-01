from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime

no_cache = 1


def get_context(context):
    params = frappe.form_dict
    if('order' in params):
        context.packOrder = frappe.get_doc('Packaging Order', params.order)
        context.packItem=frappe.get_doc('Packaging Item',context.packOrder.packaging_item);
        context.packagingOrderShipment=frappe.get_all('Shipment Order',fields=['tracking_number','carrier_company','shipping_date','expected_delivery_date','shipping_price','html_tracking_link'],filters={'packaging_order_id':params.order})
    

    context.roles = frappe.get_roles(frappe.session.user)
    context.isPackVendor = "Packaging Vendor" in context.roles
    return context