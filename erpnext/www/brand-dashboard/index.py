from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list


no_cache = 1


def get_context(context):
    if frappe.session.user == 'Guest':
        frappe.throw(
            _("You need to be logged in to access this page"), frappe.PermissionError)
    user = frappe.get_doc('User', frappe.session.user)

    brand = user.brand_name
    context.brand_name=brand
    context.username = frappe.get_doc('User', frappe.session.user).full_name

    context.shipmentOrdersList = frappe.get_all('Shipment Order',filters={'docstatus':0,'brand':brand}, fields=['internal_ref_prod_order',
                                                'internal_ref', 'product_order_id','fabric_order_id','trimming_order_id','packaging_order_id','shipping_document','html_tracking_link','shipping_date','carrier_company','tracking_number','expected_delivery_date','name', 'docstatus','stock'])



    context.fabricReminders = frappe.db.sql(
        'select r.order,o.fabric_vendor,o.confirmation_reminder,o.profoma_reminder,o.payment_reminder,o.shipment_reminder,o.reception_reminder,r.type,r.seen,o.internal_ref,r.name from `tabReminder` r inner join `tabFabric Order` o on r.order=o.name where brand=%s',brand)

    context.trimmingReminders = frappe.db.sql(
        'select r.order,o.trimming_vendor,o.confirmation_reminder,o.profoma_reminder,o.payment_reminder,o.shipment_reminder,o.reception_reminder,r.type,r.seen,o.internal_ref,r.name from `tabReminder` r inner join `tabTrimming Order` o on r.order=o.name where brand=%s',brand)

    context.packReminders = frappe.db.sql(
        'select r.order,o.packaging_vendor,o.confirmation_reminder,o.profoma_reminder,o.payment_reminder,o.shipment_reminder,o.reception_reminder,r.type,r.seen,o.internal_ref,r.name from `tabReminder` r inner join `tabPackaging Order` o on r.order=o.name where brand=%s',brand)

    context.fabCount = frappe.db.sql(
        "SELECT COUNT(name) FROM tabReminder WHERE seen='0' and order_type='fabric'")

    context.trimCount = frappe.db.sql(
        "SELECT COUNT(name) FROM tabReminder WHERE seen='0' and order_type='trimming'")

    context.packCount = frappe.db.sql(
        "SELECT COUNT(name) FROM tabReminder WHERE seen='0' and order_type='packaging'")

    # fabricReminderList=getFabricReminders(fabricReminders);
    # trimmingReminderList=getTrimmingReminders(trimmingReminders);
    # packReminderList=getPackReminders(packReminders);

    return context
