import frappe
import json


@frappe.whitelist()
def updateStock(stock_name, quantity, old_quantity, description, price):
    quantity = int(quantity)
    old_quantity = int(old_quantity)
    if quantity > old_quantity:
        amount = quantity-old_quantity
        stockIn(stock_name, amount, quantity, description)
    elif old_quantity > quantity:
        amount = old_quantity-quantity
        stockOut(stock_name, amount, quantity, description)
    else:
        pass

    updateQuantity(stock_name, quantity, price)


@frappe.whitelist()
def directShip(stock_name, amount, old_stock, description, price):
    new_stock = int(old_stock)-int(amount)

    stockOut(stock_name, amount, new_stock, description)
    updateQuantity(stock_name, new_stock, price)


@frappe.whitelist()
def shipFromExisting(stock_name, amount, old_stock, description, price):
    new_stock = int(old_stock)+int(amount)

    stockIn(stock_name, amount, new_stock, description)
    updateQuantity(stock_name, new_stock, price)


@frappe.whitelist()
def get_purchase(client):

    purchase = frappe.get_list("Sales Order", filters={
        "customer": client})

    return purchase


@frappe.whitelist()
def get_fabric_orders(vendor):

    orders = frappe.get_list("Fabric Order", filters={
        "fabric_vendor": vendor})

    return orders


@frappe.whitelist()
def get_trimming_orders(vendor):

    orders = frappe.get_list("Trimming Order", filters={
        "trimming_vendor": vendor})

    return orders


@frappe.whitelist()
def get_packaging_orders(vendor):

    orders = frappe.get_list("Packaging Order", filters={
        "packaging_vendor": vendor})

    return orders


@frappe.whitelist()
def get_purchase_items(purchase):

    order = frappe.get_doc('Sales Order', purchase)
    qtys = {}
    for i in order.items:
        item_name = frappe.db.get_value("Item", i.item_name, 'item_name')

        qtys[item_name] = frappe.get_list(
            'Quantity Per Size', filters={'order_id': i.name}, fields=['size', 'quantity'], order_by='creation asc')

    return qtys


@frappe.whitelist()
def get_qps(purchase):
    query = """select i.item_name,qpz.size,qpz.quantity
    from `tabSales Order Item` soi
    left join `tabItem` i on soi.item_name = i.name
    right join `tabQuantity Per Size` qpz on soi.name = qpz.order_id
    where soi.parent = %s
    order by i.item_name"""

    qps = frappe.db.sql(query, purchase)

    temp = {}
    for i in qps:
        if i[0] not in temp:
            temp[i[0]] = []
        temp[i[0]].append(i)

    return {"quantities": temp}


@frappe.whitelist()
def get_order_details_fabric(order):
    fabric_order = frappe.get_doc('Fabric Order', order)
    # need to get the name of the stock for fabric (fabric_order.fabric_ref)
    # and put it to (fabric_stock_name)

    fabric_stock_name = frappe.get_all('Stock', filters={
                                       'item_type': 'fabric', 'internal_ref': fabric_order.fabric_ref}, fields=['name'])
    fabric_stock = frappe.get_doc('Stock', fabric_stock_name)

    return{"fabric_ref": fabric_order.fabric_ref, "quantity": fabric_order.quantity, "stock_name": fabric_stock.name, "old_stock": fabric_stock.quantity, "price": fabric_order.price_per_unit}


@frappe.whitelist()
def get_order_details_trimming(order):
    fabric_ref = frappe.get_value('Fabric Order', order, 'fabric_ref')
    quantity = frappe.get_value('Fabric Order', order, 'quantity')

    return{"fabric_ref": fabric_ref, "quantity": quantity}


@frappe.whitelist()
def get_order_details_packaging(order):

    fabric_ref = frappe.get_value('Fabric Order', order, 'fabric_ref')
    quantity = frappe.get_value('Fabric Order', order, 'quantity')

    return{"fabric_ref": fabric_ref, "quantity": quantity}


@frappe.whitelist()
def get_status(item, requiredQuantity):
    doc = frappe.get_list('Stock', filters={'internal_ref': item}, fields=[
                          'name', 'quantity'])
    if len(doc) > 0:
        if doc[0].quantity > int(requiredQuantity):
            return {'status': frappe._("In Stock")}
        else:
            return {'status': frappe._("No Stock")}

    return {'status': frappe._("Enter quantities")}


def get_details_fabric_from_order(order):
    # returns fabric details of the stock from an order
    if order.fabric_ref == None:
        return None
    fabric_stock_name = frappe.get_all('Stock', filters={
                                       'item_type': 'fabric', 'internal_ref': order.fabric_ref}, fields=['name'])
    if fabric_stock_name == None or len(fabric_stock_name) == 0:
        return None
    fabric_stock = frappe.get_doc('Stock', fabric_stock_name[0].name)
    fabric_item = frappe.get_doc(
        'Fabric', order.fabric_ref)

    return{"fabric_ref": order.fabric_ref, "stock_name": fabric_stock.name, "old_stock": fabric_stock.quantity, "unit_price": fabric_item.unit_price, 'old_value': fabric_stock.total_value}


def get_details_trimming_from_order(order, order_type):
    trimming_item = None
    if order_type == "prototype":
        trimming_item = order.trimming_item
    elif order_type == "production":
        trimming_item = order.trimming
    # returns trimmng details of the stock from any kind of order from prototype and production

    if trimming_item == None:
        return None

    trimming_item = frappe.get_all('Trimming Item', filters={
                                   'name': trimming_item}, fields=['internal_ref', 'unit_price'])

    trimming_stock_name = frappe.get_all('Stock', filters={
        'item_type': 'trimming', 'internal_ref': trimming_item[0].internal_ref}, fields=['name'])
    if trimming_stock_name == None or len(trimming_stock_name) == 0:
        return None
    trimming_stock = frappe.get_doc('Stock', trimming_stock_name[0].name)

    return{"trimming_ref": trimming_item, "stock_name": trimming_stock.name, "old_stock": trimming_stock.quantity, "unit_price": trimming_item[0].unit_price, 'old_value': trimming_stock.total_value}


def get_details_packaging_from_order(order, order_type):
    # returns packaging details of the stock from any kind of order from prototype and production
    packaging_item = None
    if order_type == "production":
        packaging_item = order.packaging

    if packaging_item == None:
        return None

    packaging_item = frappe.get_all('Packaging Item', filters={
                                    'name': packaging_item}, fields=['internal_ref', 'unit_price'])

    packaging_stock_name = frappe.get_all('Stock', filters={
        'item_type': 'packaging', 'internal_ref': packaging_item[0].internal_ref}, fields=['name'])
    if packaging_stock_name == None or len(packaging_stock_name) == 0:
        return None
    packaging_stock = frappe.get_doc('Stock', packaging_stock_name[0].name)

    return{"trimming_ref": packaging_item, "stock_name": packaging_stock.name, "old_stock": packaging_stock.quantity, "unit_price": packaging_item[0].unit_price, 'old_value': packaging_stock.total_value}


def get_product_details_from_order(order, order_type):
    # returns product type details of the stock from any kind of order from prototype and production
    product = None
    if order_type == "prototype":
        product = order.product
    elif order_type == "production":
        product = order.product_name
    if product == None:
        return None
    production_stock_name = frappe.get_all('Stock', filters={
        'item_type': 'product', 'product': product}, fields=['name'])
    if production_stock_name == None or len(production_stock_name) == 0:
        return None
    production_stock = frappe.get_doc('Stock', production_stock_name[0].name)
    return {'stock_name': production_stock_name[0].name, 'old_stock': production_stock.quantity, 'old_value': production_stock.total_value}


def createNewProductStock(doc, method):

    total_value = int(doc.avg_price)*0
    docStock = frappe.get_doc({
        "doctype": "Stock",
        "item_type": 'product',
        "product": doc.name,
        "parent": doc.name,
        "quantity": 0,
        "total_value": total_value
    })
    docStock.insert()
    frappe.db.commit()


def createNewFabricStock(doc, method):

    docStock = frappe.get_doc({
        "doctype": "Stock",
        "item_type": 'fabric',
        "internal_ref": doc.name,
        "parent": doc.name,
        "quantity": 0,
        "total_value": 0,
    })
    docStock.insert()
    frappe.db.commit()


def createNewTrimmingStock(doc, method):

    docStock = frappe.get_doc({
        "doctype": "Stock",
        "item_type": 'trimming',
        "internal_ref": doc.name,
        "parent": doc.name,
        "quantity": 0,
        "total_value": 0,
    })
    docStock.insert()
    frappe.db.commit()


def createNewPackagingStock(doc, method):

    docStock = frappe.get_doc({
        "doctype": "Stock",
        "item_type": 'packaging',
        "internal_ref": doc.name,
        "parent": doc.name,
        "quantity": 0,
        "total_value": 0,
    })
    docStock.insert()
    frappe.db.commit()


def stockIn(stock_name, amount, quantity, description):
    doc = frappe.get_doc({
        "doctype": "Stock History",
        "parent": stock_name,
        "parentfield": "name",
        "parenttype": "Stock",
        "in_out": "in",
        "quantity": amount,
        "stock": quantity,
        "description": description
    })
    doc.insert()
    frappe.db.commit()


def stockOut(stock_name, amount, quantity, description):
    doc = frappe.get_doc({
        "doctype": "Stock History",
        "parent": stock_name,
        "parentfield": "name",
        "parenttype": "Stock",
        "in_out": "out",
        "quantity": amount,
        "stock": quantity,
        "description": description
    })
    doc.insert()
    frappe.db.commit()


def updateQuantity(stock_name, quantity, price):
    total_value = float(quantity)*float(price)
    frappe.db.set_value('Stock', stock_name, {
        'quantity': quantity,
        'total_value': total_value
    })

    frappe.db.commit()


def updateStock2(stock_name, quantity, old_quantity, description, price):
    quantity = int(quantity)
    if(old_quantity == None):
        old_quantity = frappe.get_doc('Stock', stock_name).quantity
    else:
        old_quantity = int(old_quantity)

    if quantity > old_quantity:
        amount = quantity-old_quantity
        stockIn(stock_name, amount, quantity, description)
    elif old_quantity > quantity:
        amount = old_quantity-quantity
        stockOut(stock_name, amount, quantity, description)
    else:
        pass

    updateQuantity(stock_name, quantity, price)


def get_total_quantity(order):
    # this functio returns total quantity of the order collecting all size quantities
    total_quantity = 0
    for size in order.quantity_per_size:
        if (size.quantity != None):
            total_quantity = total_quantity + int(size.quantity)
    return total_quantity


def calculate_price(products):
    # request format,
    #  products = {'0001':{'XS':1,'S':2},'0002':{'M':3}}

    # response format
    # { '0001':233123,'0002':3424324, 'total':321321313}

    prices = {}
    perpiece = {}
    for p in products:
        prices[p] = 0
        for s in products[p]:
            qty = products[p][s]
            price = frappe.get_list('Prices for Quantity', filters={
                                    'parent': p, 'from': ['<=', qty], 'to': ['>=', qty]}, fields=['price'])
            if(len(price) > 0):
                prices[p] += price[0]['price']*float(qty)
                perpiece[p] = price[0]['price']

    total = 0
    for p in prices:
        total += float(prices[p])
    prices['total'] = total
    prices['perpiece'] = perpiece
    return prices


def get_size_sales_order(sales_order):
    # this returns a dictionary of size quantities with product name
    # output of this function can be used in calculate_price function
    size_order = {}
    size_order.update([(order.item_code, {})])
    for size in order.quantity_per_size:
        size_order[order.product_name].update(
            [(size.size, int(size.quantity))])
    return size_order


# decrease item quantity from stock
def updateShipmentorderStocks(doc, method):
    sales_order_item = frappe.get_doc('Sales Order Item', doc.product_order_id)
    # sales_order_item.docstatus = 3
    # sales_order_item.save()
    # frappe.db.commit()
    quantity = get_total_quantity(sales_order_item)
    if quantity != 0 and sales_order_item.item_code != None:
        production_stock_name = frappe.get_all(
            'Stock', filters={'item_type': 'product', 'product': sales_order_item.item_code}, fields=['name'])
        if production_stock_name != None and len(production_stock_name) != 0:
            production_stock = frappe.get_doc(
                'Stock', production_stock_name[0].name)
            total_price = production_stock.total_value - \
                calculate_price(get_size_sales_order(sales_order_item))[
                    sales_order_item.item_code]
            final_quantity = production_stock.quantity-quantity
            updateStock2(production_stock_name[0].name, final_quantity, production_stock.quantity, "Shipment Order", float(
                total_price)/final_quantity)


@frappe.whitelist()
def get_stock(item_type, ref):
    try:
        return frappe.get_all('Stock', filters={'item_type': item_type, 'internal_ref': ref}, fields=['quantity'])[0]
    except:
        return {'quantity': 0}
