import frappe
import json
import ast
import datetime
import stripe
from datetime import date, datetime

# This is your real test secret API key.

stripe.api_key = "sk_test_51HPL2BGjxNLAb2efZFPiLxejZs31yp8LAVjxg3lzmoxerCjU7SZSr9SKzCBCkQMRjIMv4rQAHbl7wsEbqKr2nDUK00xtPJpeGl"




@frappe.whitelist()
def savePaymentPlan(data,trial_period):
    data = json.loads(data)
    trial_period_array=frappe.get_all('System Data',filters={'type':'brand-trial-period'})
    trial_periodOb=frappe.get_doc('System Data',trial_period_array[0].name)
    trial_periodOb.value=trial_period
    trial_periodOb.save()

    for planName, planData in data.items():
        if(planName != ''):
            plan = frappe.get_doc("Payment Plan", data[planName]['name'])
            plan.plan_name = planName
            plan.annual_price = data[planName]['Pricing-Annual']
            plan.monthly_price = data[planName]['Pricing-Month']
            plan.no_of_clients=data[planName]['No of Accesses ']
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

def calculate_order_amount(data):
    payment_plan=frappe.get_doc('Payment Plan',data['plan_name'])
    if(data['plan_period']=='Monthly'):
        payment=payment_plan.monthly_price
    elif(data['plan_period']=='Annually'):
        payment=payment_plan.annual_price

    payment=int(payment*100)
    
    # Replace this constant with a calculation of the order's amount

    # Calculate the order total on the server to prevent

    # people from directly manipulating the amount on the client

    return payment

@frappe.whitelist()
def create_payment(data):
    try:

        data = json.loads(data)
        intent = stripe.PaymentIntent.create(
            amount=calculate_order_amount(data),
            currency='usd'
        )
        return{
          'clientSecret': intent['client_secret']
        }

    except Exception as e:
        return {'error':403}

@frappe.whitelist()
def completeSubscription(data):
    data = json.loads(data)
    brandName=frappe.get_doc('User', frappe.session.user).brand_name
    brand=frappe.get_doc('Company',brandName)
    brand.subscription_period=data['plan_period']
    brand.subscribed_date=datetime.now()
    brand.subscribed_plan=data['plan_name']
    brand.enabled=1
    brand.save()
    frappe.db.commit()
    return {'Status':'Ok'}



