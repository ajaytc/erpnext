import frappe


@frappe.whitelist()
def get_customer(email):
    try:
        return frappe.get_all('Customer', filters={'email_address': email})[0].name
    except:
        frappe.throw(frappe._("Error"))
