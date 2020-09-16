import frappe
import json
import ast
import datetime


@frappe.whitelist()
def savePaymentPlan(data):
    data = json.loads(data)

    for planName, planData in data.items():
        if(planName != ''):
            plan = frappe.get_doc("Payment Plan", data[planName]['name'])
            plan.plan_name = planName
            plan.annual_price = data[planName]['Pricing-Annual']
            plan.monthly_price = data[planName]['Pricing-Month']
            plan.no_of_clients=data[planName]['No of Accesses ']
            plan.trial_days = data[planName]['Days of Trial']
            plan.client = data[planName]['Client']
            plan.supply = data[planName]['Supply']
            plan.pre_production = data[planName]['Pre Production']
            plan.shipment = data[planName]['Shipment']
            plan.stock = data[planName]['Stock']
            plan.snf = data[planName]['S&F']
            plan.production = data[planName]['Production']

            plan.save()
            frappe.db.commit()
    return {'status': 'ok', 'plan': plan}
