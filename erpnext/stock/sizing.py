import frappe


@frappe.whitelist()
def getSizes(item):
    sizes = frappe.db.sql(
        """ select distinct s.size from tabItem i left join `tabSizing` s on i.sizing = s.parent where s.size is not null order by s.idx""")
    temp = []

    for s in sizes:
        temp.append(s[0])
    return {"sizes": temp}
