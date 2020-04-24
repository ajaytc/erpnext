import frappe
import json

@frappe.whitelist()
def submit_trim_vendor_summary_info(data):
    data=json.loads(data);
    trimOrder = frappe.get_doc('Trimming Order', data['order']);
    trimOrder.ex_work_date=data['ex_work_date'];
    trimOrder.confirmation_doc=data['confirmation_doc'];
    trimOrder.profoma=data['profoma'];
    trimOrder.invoice=data['invoice'];
    trimOrder.carrier=data['carrier'];
    trimOrder.tracking_number=data['tracking_number'];
    trimOrder.shipment_date=data['shipment_date'];
    trimOrder.production_comment=data['production_comment'];
    trimOrder.save()
    
    return trimOrder;

@frappe.whitelist()
def submit_payment_proof(data):
    data=json.loads(data);
    trimOrder = frappe.get_doc('Trimming Order', data['order']);
    trimOrder.payment_proof=data['payment_proof'];
    trimOrder.comment=data['comment'];
    trimOrder.save();
    frappe.db.commit();
    
    

    return trimOrder;