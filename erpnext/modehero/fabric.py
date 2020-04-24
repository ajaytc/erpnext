import frappe
import json

@frappe.whitelist()
def submit_fabric_vendor_summary_info(data):
    data=json.loads(data);
    fabricOrder = frappe.get_doc('Fabric Order', data['order']);
    fabricOrder.ex_work_date=data['ex_work_date'];
    fabricOrder.confirmation_doc=data['confirmation_doc'];
    fabricOrder.profoma=data['profoma'];
    fabricOrder.invoice=data['invoice'];
    fabricOrder.carrier=data['carrier'];
    fabricOrder.tracking_number=data['tracking_number'];
    fabricOrder.shipment_date=data['shipment_date'];
    fabricOrder.production_comment=data['production_comment'];
    fabricOrder.save()
    
    return fabricOrder;

@frappe.whitelist()
def submit_payment_proof(data):
    data=json.loads(data);
    fabricOrder = frappe.get_doc('Fabric Order', data['order']);
    fabricOrder.payment_proof=data['payment_proof'];
    fabricOrder.comment=data['comment'];
    fabricOrder.save();
    frappe.db.commit();
    
    

    return fabricOrder;