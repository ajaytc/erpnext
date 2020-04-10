import frappe

@frappe.whitelist()
def getQuantities(item):

    quantities = frappe.db.sql("""select so.customer ,qps.size ,qps.quantity from `tabSales Order Item` soi right join `tabSales Order` so on soi.parent=so.name left join `tabQuantity Per Size` qps on qps.order_id=soi.name where soi.item_code=item AND so.docstatus = 0 """)

    return  {"quantities": quantities}
