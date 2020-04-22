import frappe


@frappe.whitelist()
def get_brand(user):
    return frappe.get_doc('User', user).brand_name
