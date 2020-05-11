import frappe
import json


@frappe.whitelist()
def create_destination(data):
    data = json.loads(data)
    item = frappe.get_doc({
        'doctype': 'Destination',
        'destination_name': data['name'],
        'email_address': data['email'],
        'address_line_1': data['address1'],
        'address_line_2': data['address2'],
        'contact': data['contact'],
        'phone': data['phone_number'],
        'city_town': data['city'],
        'postal_code': data['zip_code'],
        'client_name': data['customer'],
    })
    item.insert()
    frappe.db.commit()
    return {'status': 'ok', 'item': item}
