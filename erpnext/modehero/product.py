import frappe
import json


@frappe.whitelist()
def get_products_of_category(category):
    return frappe.get_list('Item', filters={'item_group': category}, fields=['name', 'item_name'])


@frappe.whitelist()
def get_item_code():
    items = frappe.get_list(
        'Item', order_by='creation desc', fields=['item_code'])
    return int(items[0].item_code)+1
