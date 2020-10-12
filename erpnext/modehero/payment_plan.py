import frappe
import json
import ast
import datetime
import stripe
from datetime import date, datetime,timedelta

# This is your real test secret API key.

stripe.api_key = "sk_test_51HPL2BGjxNLAb2efZFPiLxejZs31yp8LAVjxg3lzmoxerCjU7SZSr9SKzCBCkQMRjIMv4rQAHbl7wsEbqKr2nDUK00xtPJpeGl"


@frappe.whitelist()
def savePaymentPlan(data, trial_period):
    data = json.loads(data)
    trial_period_array = frappe.get_all(
        'System Data', filters={'type': 'brand-trial-period'})
    trial_periodOb = frappe.get_doc('System Data', trial_period_array[0].name)
    trial_periodOb.value = trial_period
    trial_periodOb.save()

    for planName, planData in data.items():
        if(planName != ''):
            plan = frappe.get_doc("Payment Plan", data[planName]['name'])
            plan.plan_name = planName
            plan.annual_price = data[planName]['Pricing-Annual']
            plan.monthly_price = data[planName]['Pricing-Month']
            plan.no_of_clients = data[planName]['No of Accesses ']
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
    payment_plan = frappe.get_doc('Payment Plan', data['plan_name'])
    if(data['plan_period'] == 'Monthly'):
        payment = payment_plan.monthly_price
    elif(data['plan_period'] == 'Annually'):
        payment = payment_plan.annual_price

    brandUser=frappe.get_doc('User', frappe.session.user)
    if(brandUser.country=='France'):
        vat=20
    else:
        vat=0
    planPrice=payment
    vatAmount=float(payment)*(vat/100)
    fullPayment = float(payment)+float(vatAmount)
    fullPayment=int(fullPayment*100)

    # Replace this constant with a calculation of the order's amount

    # Calculate the order total on the server to prevent

    # people from directly manipulating the amount on the client

    return fullPayment,planPrice


@frappe.whitelist()
def create_payment(data):
    try:
        
        data = json.loads(data)
        amountPrice,planPrice=calculate_order_amount(data)
        intent = stripe.PaymentIntent.create(
            amount=amountPrice,
            currency='usd'
        )
        return{
          'clientSecret': intent['client_secret'],
          'amount':planPrice,
          'fullpayment':float(amountPrice/100)
        }

    except Exception as e:
        return {'error': 403}


@frappe.whitelist()
def completeSubscription(data):
    dateformat = '%d/%m/%Y'
    data = json.loads(data)
    brandName = frappe.get_doc('User', frappe.session.user).brand_name
    brand = frappe.get_doc('Company', brandName)
    
    if(brand.subscription_end_date != None):
        brand.subscription_end_date = getNewExpireDate(data, brand)
    else:
        newSubscribedPeriod=getSubscriptionPeriod(data['plan_period'])
        trialPeriod=frappe.get_all("System Data",filters={'type':'brand-trial-period'},fields=['value'])[0]
        
        brand.subscription_end_date= datetime.strptime(frappe.format(brand.creation, 'Date'), dateformat) +timedelta(days=int(trialPeriod['value']))+timedelta(days=newSubscribedPeriod)

    brand.subscription_period = data['plan_period']
    brand.subscribed_date = datetime.now()
    brand.subscribed_plan = data['plan_name']
    paymentPlan=frappe.get_doc('Payment Plan',data['plan_name'])
    brand.client=paymentPlan.client
    brand.supply=paymentPlan.supply
    brand.production=paymentPlan.production
    brand.pre_production=paymentPlan.pre_production
    brand.shipment=paymentPlan.shipment
    brand.stock=paymentPlan.stock
    brand.snf=paymentPlan.snf
    brand.no_of_clients=paymentPlan.no_of_clients
    brand.amount=data['amount']
    brand.fullpayment=data['fullpayment']

    brand.enabled = 1
    brand.save()
    frappe.db.commit()
    return {'Status': 'Ok'}


def getNewExpireDate(data, brand):
    dateformat = '%d/%m/%Y'
    allow_period = data['plan_period']

    newSubscribedPeriod=getSubscriptionPeriod(allow_period)
    
    endSubscriptionDate=datetime.strptime(frappe.format(brand.subscription_end_date, 'Date'), dateformat)
    if(endSubscriptionDate >datetime.now()):
        newExpireDate= endSubscriptionDate +timedelta(days=newSubscribedPeriod)  
    else:
        newExpireDate=datetime.now()+timedelta(days=newSubscribedPeriod)  


    return newExpireDate  

def getSubscriptionPeriod(allow_period):
    if(allow_period == 'Monthly'):
        newSubscribedPeriod = 30
    elif(allow_period=='Annually'):
        newSubscribedPeriod=365

    return newSubscribedPeriod