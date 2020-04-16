import frappe
import json


@frappe.whitelist()
def stockIn(stock_name,amount,quantity,description):
    doc = frappe.get_doc({
	"doctype": "Stock History",
    "parent": stock_name,
    "parentfield": "name",
    "parenttype":"Stock",
	"in_out": "In",
	"quantity": amount,
    "stock": quantity,
    "_comments": description
    })
    doc.insert()
    frappe.db.commit()
    
def stockOut(stock_name,amount,quantity,description):
    doc = frappe.get_doc({
	"doctype": "Stock History",
    "parent": stock_name,
    "parentfield": "name",
    "parenttype":"Stock",
	"in_out": "Out",
	"quantity": amount,
    "stock": quantity,
    "_comments": description
    })
    doc.insert()
    frappe.db.commit()


def updateQuantityProduct(stock_name,quantity):
    frappe.db.set_value('Stock',stock_name, {
    'quantity': quantity
    }
    )
    frappe.db.commit()

@frappe.whitelist()
def updateStock(stock_name,quantity,old_quantity,description):

    if quantity > old_quantity:
        amount = int(quantity)-int(old_quantity)
        stockIn(stock_name,amount,quantity,description)
    if old_quantity > quantity:
        amount = int(old_quantity)-int(quantity)
        stockOut(stock_name,amount,quantity,description)
    else:
        pass

    updateQuantityProduct(stock_name,quantity)
