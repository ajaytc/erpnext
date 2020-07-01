from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime

no_cache = 1


def get_context(context):
    params = frappe.form_dict
    if('order' in params):
        context.trimOrder = frappe.get_doc('Trimming Order', params.order)
        context.trimmingItem=frappe.get_doc('Trimming Item',context.trimOrder.trimming_item);
        context.trimmingOrderShipment=frappe.get_all('Shipment Order',fields=['tracking_number','carrier_company','shipping_date','expected_delivery_date','shipping_price','html_tracking_link'],filters={'trimming_order_id':params.order})
    

    context.roles = frappe.get_roles(frappe.session.user)
    context.isTrimVendor = "Trimming Vendor" in context.roles
    return context