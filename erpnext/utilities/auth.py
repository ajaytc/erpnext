import frappe


@frappe.whitelist()
def get_roles_of_user():
    result = frappe.db.sql(
        "select  * from tabUser u left join `tabHas Role` hr on u.name = hr.parent where u.name = '" + frappe.session.user + "'")

    roles = []
    for i in result:
        roles.append(i[70])

    return roles
