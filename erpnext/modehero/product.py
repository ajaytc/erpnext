import frappe
import json


@frappe.whitelist()
def get_products_of_category(category):
    return frappe.get_list('Item', filters={'item_group': category}, fields=['name', 'item_name'])


@frappe.whitelist()
def get_item_code():
    items = frappe.get_all(
        'Item', order_by='creation desc', fields=['item_code'])
    return int(items[0].item_code)+1


@frappe.whitelist()
def create_product_category(data):
    data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    item = frappe.get_doc({
        'doctype': 'Item Group',
        'brand_name': brand,
        'item_group_name': data['name'],
    })
    item.insert()
    frappe.db.commit()
    return {'status': 'ok', 'item': item}


@frappe.whitelist()
def create_garmentlabel(data):
    data = json.loads(data)
    item = frappe.get_doc({
        'doctype': 'Garment Label',
        'customer': brand,
        'label_name': data['label_name'],
        'label': data['label'],
    })
    item.insert()
    frappe.db.commit()
    return {'status': 'ok', 'item': item}
