from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime
from erpnext.modehero.user import haveAccess
from erpnext.modehero.dispatch_bulk import collect_item_destination_data,add_size_quantity_data,add_sent_data,modify_order_list

no_cache = 1
free_size_name = "Free Size"

def get_context(context):
    if frappe.session.user == 'Guest':
        frappe.throw(
            _("You need to be logged in to access this page"), frappe.PermissionError)
    module = 'stock'
    if(not haveAccess(module)):
        frappe.throw(_("You have not subscribed to this service"),
                     frappe.PermissionError)
    roles = frappe.get_roles(frappe.session.user)

    if ("Administrator" not in roles) and ("Brand User" not in roles):
        frappe.throw(_("Not Permitted!"), frappe.PermissionError)

    brand = frappe.get_doc('User', frappe.session.user).brand_name
    orders = frappe.db.sql("""select soi.name,po.name,po.destination_type,soi.item_destination,po.final_destination,po.product_name,po.production_factory,po.carrier,po.tracking_number,po.shipment_date,po.creation,soi.creation,po.internal_ref,soi.parent from `tabProduction Order` po left join `tabSales Order Item`soi on po.name=soi.prod_order_ref and soi.docstatus=%s where po.brand=%s and po.docstatus in (%s,%s)  order by po.creation desc""", ("1",brand,"0","1"))
    # 0 = sales_order_item_name
    context.soi_name_index = 0
    # 1 = production_order_name
    # 2 = production_order_destination_type
    # 3 = sales_order_item_destination
    # 4 = production_order_destiantion
    # 5 = product_name
    # 6 = production_factory
    # 7 = carrier_number
    # 8 = tracking_number
    # 9 = shipment_date
    # 10 = po_creation_time
    context.po_creation_time_index = 10
    # 11 = soi_creation_time
    context.soi_creation_time_index = 11
    # 12 = po_internal_ref
    context.if_index = 12
    # 13 = soi_parent_name
    context.soi_parent_index = 13
    # 14 = item_name
    context.item_name_index = 14
    # 15 = item_sizes
    context.sizes_scheme_index = 15
    # 16 = current_stock_sizes_quantities
    context.stock_qty_index = 16
    # 17 = order_size_details
    context.order_qty_index = 17
    # 18 = sent_history
    context.sent_history_index = 18
    # 19 = current_active_shipment 
    context.current_active_shipment_index = 19
    # 20 = POS_or_DESTINY
    # 21 = is_tickable
    context.is_tickable_index = 21

    orders = list(orders)
    for i in range(len(orders)):
        orders[i] = list(orders[i])
    pos_destination_support_data,item_support_data = collect_item_destination_data(orders)
    orders_with_quantity_data = add_size_quantity_data(orders,item_support_data)
    final_order_list = add_sent_data(orders_with_quantity_data,brand)
    context.presenting_order_data = modify_order_list(final_order_list,pos_destination_support_data)

    return context

