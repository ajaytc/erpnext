import frappe


@frappe.whitelist()
def get_customer(email):
    try:
        return frappe.get_all('Customer', filters={'email_address': email})[0].name
    except:
        frappe.throw(frappe._("Error"))

@frappe.whitelist()
def get_branded_companies():
    brand = frappe.get_doc('User', frappe.session.user).brand_name
    company_objs = frappe.get_all('Customer',filters={'brand':brand},fields=['name'])
    result = []
    for x in company_objs:
        result.append({
            'label':x.name,
            'value':x.name
        })
    return result