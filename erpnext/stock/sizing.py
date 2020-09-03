import frappe


@frappe.whitelist()
def getSizes(item):
    sizes = frappe.db.sql(
        """ select distinct s.size from tabItem i left join `tabSizing` s on i.sizing = s.parent where s.size is not null and i.name = """+item+""" order by s.idx""")
    temp = []

    for s in sizes:
        temp.append(s[0])
    return {"sizes": temp}


@frappe.whitelist()
def getSizesFromStock(stock):
    stockOb = frappe.get_doc('Stock', stock)
    sizes = getSizes(stockOb.product)
    return sizes
