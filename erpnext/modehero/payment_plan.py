import frappe
import json
import ast
import datetime
import stripe

# This is your real test secret API key.

stripe.api_key = "sk_test_51HPL2BGjxNLAb2efZFPiLxejZs31yp8LAVjxg3lzmoxerCjU7SZSr9SKzCBCkQMRjIMv4rQAHbl7wsEbqKr2nDUK00xtPJpeGl"




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

def calculate_order_amount(items):
    
    # Replace this constant with a calculation of the order's amount

    # Calculate the order total on the server to prevent

    # people from directly manipulating the amount on the client

    return 1400

@frappe.whitelist()
def create_payment(data):
    try:

        data = json.loads(data)
        intent = stripe.PaymentIntent.create(
            amount=calculate_order_amount(data['items']),
            currency='usd'
        )
        return{
          'clientSecret': intent['client_secret']
        }

    except Exception as e:
        return {'error':403}