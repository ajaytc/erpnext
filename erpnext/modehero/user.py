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
def test_deactivate():
    return auto_deactivate()
