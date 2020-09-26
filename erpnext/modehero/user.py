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

def auto_deactivate_brands():
    print('running brands deactivation cron')
    brands = frappe.get_all('Company')
    dateformat = '%d-%m-%Y'
    for brand_name in brands:
        brand = frappe.get_doc('Company', brand_name)
        if brand.enabled == '1':
            spent_duration = datetime.now() - datetime.strptime(frappe.format(brand.subscribed_date, 'Date'), dateformat)
            if(brand.subscription_period=='Monthly'):
                allowed_duration=30
            elif(brand.subscription_period=='Annually'):
                allowed_duration=365
            if spent_duration.days > allowed_duration:
                brand.enabled = 0
                brand.save()
                print('disable user', brand.name)
    return {'status': 'ok'}


@frappe.whitelist()
def test_deactivate():
    return auto_deactivate()
