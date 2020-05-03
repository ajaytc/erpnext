import frappe
import json
import ast


@frappe.whitelist()
def create_factory(data):
    data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    factory = frappe.get_doc({
        'doctype': 'Production Factory',
        'brand': brand,
        'email_address': data['email'],
        'address_line_1': data['address1'],
        'address_line_2': data['address2'],
        'contact': data['contact'],
        'phone': data['phone_number'],
        'city_town': data['city'],
        'zip_code': data['zip_code'],
        'factory_name': data['name']
    })
    factory.insert()
    frappe.db.commit()
    return {'status': 'ok', 'factory': factory}
