import frappe
import json


@frappe.whitelist()
def submit_pack_vendor_summary_info(data):
    data = json.loads(data)
    packOrder = frappe.get_doc('Packaging Order', data['order'])
    packOrder.ex_work_date = data['ex_work_date']
    packOrder.confirmation_doc = data['confirmation_doc']
    packOrder.profoma = data['profoma']
    packOrder.invoice = data['invoice']
    packOrder.carrier = data['carrier']
    packOrder.tracking_number = data['tracking_number']
    packOrder.shipment_date = data['shipment_date']
    packOrder.production_comment = data['production_comment']
    if(packOrder.confirmation_doc != 'None' or packOrder.profoma != 'None' or packOrder.invoice != 'None' or packOrder.ex_work_date):
        packOrder.docstatus = 4
    if(packOrder.carrier or packOrder.tracking_number or packOrder.shipment_date):
        packOrder.docstatus = 3
    packOrder.save()

    return packOrder


@frappe.whitelist()
def submit_payment_proof(data):
    data = json.loads(data)
    packOrder = frappe.get_doc('Packaging Order', data['order'])
    packOrder.payment_proof = data['payment_proof']
    packOrder.comment = data['comment']
    packOrder.save()
    frappe.db.commit()

    return packOrder
