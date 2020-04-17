import frappe
import json

@frappe.whitelist
def createNewProductStock(doc):

    total_value = int(doc.avg_price)*0
    docStock = frappe.get_doc({
	"doctype": "Stock",
    "item_type": 'product',
    "product": doc.name,
    "quantity": quantity,
    "total_value": total_value
    })
    docStock.insert()
    frappe.db.commit()



def stockIn(stock_name,amount,quantity,description):
    doc = frappe.get_doc({
	"doctype": "Stock History",
    "parent": stock_name,
    "parentfield": "name",
    "parenttype":"Stock",
	"in_out": "in",
	"quantity": amount,
    "stock": quantity,
    "description": description
    })
    doc.insert()
    frappe.db.commit()
    
def stockOut(stock_name,amount,quantity,description):
    doc = frappe.get_doc({
	"doctype": "Stock History",
    "parent": stock_name,
    "parentfield": "name",
    "parenttype":"Stock",
	"in_out": "out",
	"quantity": amount,
    "stock": quantity,
    "description": description
    })
    doc.insert()
    frappe.db.commit()

def updateQuantity(stock_name,quantity,price):
    total_value = float(quantity)*float(price)
    frappe.db.set_value('Stock',stock_name, {
    'quantity': quantity,
    'total_value': total_value
    })

    frappe.db.commit()

def updateQuantityRaw(stock_name,quantity,price):
    total_value = float(quantity)*float(price)
    frappe.db.set_value('Stock',stock_name, {
    'quantity': quantity,
    'total_value': total_value
    })
    frappe.db.commit()

@frappe.whitelist()
def updateStock(stock_name,quantity,old_quantity,description,price):

    if quantity > old_quantity:
        amount = int(quantity)-int(old_quantity)
        stockIn(stock_name,amount,quantity,description)
    if old_quantity > quantity:
        amount = int(old_quantity)-int(quantity)
        stockOut(stock_name,amount,quantity,description)
    else:
        pass

    updateQuantity(stock_name,quantity,price)

@frappe.whitelist()
def directShip(stock_name,amount,old_stock,description,price):
    new_stock = int(old_stock)-int(amount)

    stockOut(stock_name,amount,new_stock,description)
    updateQuantity(stock_name,new_stock,price)

