from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list

no_cache = 1


def get_context(context):
    context.username = frappe.get_doc('User', frappe.session.user).full_name


    context.shipmentOrdersList=frappe.get_all('Shipment Order',fields=['internal_ref','product_order_id','shipping_date','name'])

    
    return context
