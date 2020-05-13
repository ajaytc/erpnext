import frappe


@frappe.whitelist()
def get_customer(email):
    try:
        return frappe.get_all('Customer', filters={'user': email})[0].name
    except:
        frappe.throw(frappe._("Error"))
