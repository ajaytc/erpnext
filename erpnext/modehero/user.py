import frappe
import json
from datetime import date, datetime


@frappe.whitelist()
def get_brand(user):
    return frappe.get_doc('User', user).brand_name


def signup(doc, method):

    if (doc.doctype == "Customer"):
        roles = [{"role": "Customer"}]
        email = doc.email_address
        first_name = doc.customer_name

    elif (doc.doctype == "Supplier"):
        email = doc.email
        first_name = doc.supplier_name
        if (doc.supplier_group == "Packaging"):
            roles = [{"role": "Packaging Vendor"}]
        elif (doc.supplier_group == "Fabric"):
            roles = [{"role": "Fabric Vendor"}]
        elif (doc.supplier_group == "Trimming"):
            roles = [{"role": "Trimming Vendor"}]
    elif (doc.doctype == "Production Factory"):
        roles = [{"role": "Manufacturing User"}]
        email = doc.email_address
        first_name = doc.factory_name

    user = frappe.get_doc({
        "doctype": "User",
        "enabled": 1,
        "new_password": doc.password,
        "user_type": "Website User",
        "email": email,
        "first_name": first_name,
        "roles": roles
    })

    user.flags.ignore_permissions = True
    user.flags.ignore_password_policy = True
    user.insert()


def auto_deactivate():
    print('running user deactivation cron')
    users = frappe.get_all('User')
    dateformat = '%d-%m-%Y'
    for u in users:
        user = frappe.get_doc('User', u)
        if user.paid == '0':
            delta = datetime.now() - datetime.strptime(frappe.format(user.creation, 'Date'), dateformat)
            if delta.days > 14:
                user.enabled = 0
                user.save()
                print('disable user', user.name)
    return {'status': 'ok'}

@frappe.whitelist()
def auto_deactivate_brands():
    print('running brands deactivation cron')
    brands = frappe.get_all('Company')
    dateformat = '%d/%m/%Y'
    for brand_name in brands:
        brand = frappe.get_doc('Company', brand_name)
        if(inTrialPeriod(brand)):
            continue
        else:
            if(brand.enabled == 1):
                if(brand.subscription_end_date!=None):
                    if(datetime.strptime(frappe.format(brand.subscription_end_date, 'Date'), dateformat)<= datetime.now()):
                        brand.enabled = 0
                        brand.save()
                        print('disable user', brand.name)
                else:
                    brand.enabled = 0
                    brand.save()
                    print('disable user', brand.name)
    return {'status': 'ok'}

def inTrialPeriod(brand):
    dateformat = '%d/%m/%Y'
    spent_duration=datetime.now() - datetime.strptime(frappe.format(brand.creation, 'Date'), dateformat)
    trial_period=frappe.get_all("System Data",filters={'type':'brand-trial-period'},fields=['value'])
    if(spent_duration.days<=int(trial_period[0]['value'])):
        return True
    else:
        return False


@frappe.whitelist()
def test_deactivate():
    return auto_deactivate()


def haveAccess(module):
    brandName=frappe.get_doc('User', frappe.session.user).brand_name
    brand=frappe.get_doc("Company",brandName)
    subscribedPlan=frappe.get_doc("Payment Plan",brand.subscribed_plan)
    subscribedPlanDict=subscribedPlan.__dict__
    if(brand.enabled==1):
        if(inTrialPeriod(brand)):
            return True
        else:
            if(subscribedPlanDict[module]==1):
                return True
            else:
                return False
    else:
        return False
    




