import frappe
import json


# @frappe.whitelist()
# def updateStock(stock_name, quantity, old_quantity, description, price):
#     quantity = int(quantity)
#     old_quantity = int(old_quantity)
#     if quantity > old_quantity:
#         amount = quantity-old_quantity
#         stockIn(stock_name, amount, quantity, description)
#     elif old_quantity > quantity:
#         amount = old_quantity-quantity
#         stockOut(stock_name, amount, quantity, description)
#     else:
#         pass

#     updateQuantity(stock_name, quantity, price)


@frappe.whitelist()
def directShip(stock_name, amount, old_stock, description, price):
    new_stock = int(old_stock)-int(amount)

    stockOut(stock_name, amount, new_stock, description,None)
    updateQuantity(stock_name, new_stock, price,None)

@frappe.whitelist()
def directShipfromProductStock(data):
    data=json.loads(data)
    stock_name=data['stock_name']
    old_stock=data['old_stock']
    description=data['description']
    price=data['price']
    qtys=data['qtys']
    qtySizeDic={}
    amount=0
    for qty in data['qtys']:
        amount=amount+int(qty['quantity'])
        qtySizeDic[qty['size']]=qty['quantity']



    new_stock = int(old_stock)-int(amount)

    stockOut(stock_name, amount, new_stock, description,qtys)
    # stock=frappe.get_doc('Stock',stock_name)
    newSizeStocks=getNewSizewiseStock(stock_name,qtySizeDic)
    updateQuantity(stock_name, new_stock, price,newSizeStocks)

def getNewSizewiseStock(stockName,qtysDic):
    # stock=frappe.get_all('Stock',filters={'parent':stockName,'size':qtysDic.keys()},fields=['quantity','size'])
    sizeQtys=frappe.db.sql("""select sps.size,sps.quantity from `tabProduct Stock Per Size` sps where `parent`=%s and `size` in %s""",(stockName, tuple(qtysDic.keys())))
    # stock_per_size=stock.product_stock_per_size
    newQtys=[]

    for sizeqty in sizeQtys:
        newQty={}
        size=sizeqty[0]
        oldstock=int(sizeqty[1])
        newstock=oldstock-int(qtysDic[size])
        newQty['size']=size
        newQty['quantity']=newstock
        newQtys.append(newQty)
    
    return newQtys

        


@frappe.whitelist()
def shipFromExisting(stock_name, amount, old_stock, description, price):
    new_stock = int(old_stock)+int(amount)

    stockIn(stock_name, amount, new_stock, description,None)
    updateQuantity(stock_name, new_stock, price,None)


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
        trimming_item = order.trimming_ref
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
        packaging_item_name = order.packaging_ref

    if packaging_item_name == None:
        return None

    packaging_item = frappe.get_all('Packaging Item', filters={
                                    'name': packaging_item_name}, fields=['internal_ref', 'unit_price'])

    packaging_stock_name = frappe.get_all('Stock', filters={
        'item_type': 'packaging', 'internal_ref': packaging_item_name}, fields=['name'])
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
    production_stock = frappe.get_all('Stock', filters={
        'item_type': 'product', 'product': product})
    if production_stock == None or len(production_stock) == 0:
        return None
    production_stock = frappe.get_doc("Stock",production_stock[0].name)
    # this is for develeopment perposes
    if len(production_stock.product_stock_per_size)==0:
        return None
    # this is for develeopment perposes
    if order_type == "prototype":
        return {'stock_name': production_stock.name, 'old_stock': production_stock.quantity, 'old_value': production_stock.total_value,"size_details":None}
    return {'stock_name': production_stock.name, 'old_stock': production_stock.quantity, 'old_value': production_stock.total_value,"size_details":production_stock.product_stock_per_size}


def createNewProductStock(doc, method):

    total_value = int(doc.avg_price)*0
    item_doc = frappe.get_doc('Item',doc.name)
    sizings = frappe.get_all('Sizing', filters={'parent': item_doc.sizing}, fields=['size'],order_by='idx')
    size_n_qty = []
    for size in sizings:
        size_n_qty.append({"size":size.size,"quantity":0})
    docStock = frappe.get_doc({
        "doctype": "Stock",
        "item_type": 'product',
        "product": doc.name,
        "parent": doc.name,
        "quantity": 0,
        "total_value": total_value,
        "product_stock_per_size":size_n_qty
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


def stockIn(stock_name, amount, quantity, description,size_quantites):
    doc_dic = {
        "doctype": "Stock History",
        "parent": stock_name,
        "parentfield": "name",
        "parenttype": "Stock",
        "in_out": "in",
        "quantity": amount,
        "stock": quantity,
        "description": description
    }
    if size_quantites!=None:
        doc_dic["product_stock_history_per_size"] = size_quantites
    doc = frappe.get_doc(doc_dic)
    doc.insert()
    frappe.db.commit()
    return doc


def stockOut(stock_name, amount, quantity, description,size_quantites):
    doc_dic ={
        "doctype": "Stock History",
        "parent": stock_name,
        "parentfield": "name",
        "parenttype": "Stock",
        "in_out": "out",
        "quantity": amount,
        "stock": quantity,
        "description": description
    }
    if size_quantites!=None:
        doc_dic["product_stock_history_per_size"] = size_quantites
    doc = frappe.get_doc(doc_dic)
    doc.insert()
    frappe.db.commit()
    return doc


def updateQuantity(stock_name, quantity, price,size_detail):
    total_value = float(quantity)*float(price)
    stock_doc = frappe.get_doc("Stock",stock_name)
    if len(stock_doc.product_stock_per_size)==0:
        return None
    if size_detail!=None:
        for x in range(len(stock_doc.product_stock_per_size)):
            for y in range(len(size_detail)):
                if stock_doc.product_stock_per_size[x].size == size_detail[y].size:
                    stock_doc.product_stock_per_size[x].quantity = size_detail[y].quantity
    stock_doc.quantity = quantity
    stock_doc.total_value = total_value
    stock_doc.save()
    frappe.db.commit()


def updateStock2(stock_name, quantity, old_quantity, description, price,item_type,size_detail):
    # size_detail is not None only for product stocks
    quantity = int(quantity)
    if(old_quantity == None):
        old_quantity = int(frappe.get_doc('Stock', stock_name).quantity)
    else:
        old_quantity = int(old_quantity)

    if quantity > old_quantity:
        amount = quantity-old_quantity
        if size_detail !=None:
            stock_history_sizeqty = get_size_qty_history(size_detail["new_incoming"])
            stockIn(stock_name, amount, quantity, description,stock_history_sizeqty)
            size_detail = get_final_size_quantities(size_detail,"in")
        else:
            stockIn(stock_name, amount, quantity, description,None)
    elif old_quantity > quantity:
        amount = old_quantity-quantity
        if size_detail !=None:
            stock_history_sizeqty = get_size_qty_history(size_detail["new_incoming"])
            stockOut(stock_name, amount, quantity, description,stock_history_sizeqty)
            size_detail = get_final_size_quantities(size_detail,"out")
        else:
            stockOut(stock_name, amount, quantity, description,None)
    else:
        pass
    
    updateQuantity(stock_name, quantity, price,size_detail)


def get_size_qty_history(size_detail):
    doc_list = []
    for size in size_detail:
        doc = {
            "quantity": size_detail[size],
            "size": size,
        }
        doc_list.append(doc)
    return doc_list


def get_final_size_quantities(size_detail,in_or_out):
    if size_detail==None:
        return None
    old_size_qty = size_detail["old"]
    incoming_size_qty = size_detail["new_incoming"]
    for index_of_sq in range(len(old_size_qty)):
        if old_size_qty[index_of_sq].size not in incoming_size_qty:
            continue
        if in_or_out=="in":
            old_size_qty[index_of_sq].quantity = int(old_size_qty[index_of_sq].quantity) + int(incoming_size_qty[old_size_qty[index_of_sq].size])
        elif in_or_out=="out":
            old_size_qty[index_of_sq].quantity = int(old_size_qty[index_of_sq].quantity) - int(incoming_size_qty[old_size_qty[index_of_sq].size])

    return old_size_qty

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

    # here if the production order has the searching inernal ref, that is considered as a product shipping ( underlying code is to reduce product stock)
    if doc.internal_ref_prod_order!=None:
        production_order = frappe.get_doc("Production Order",doc.internal_ref_prod_order)
        if len(doc.shipment_quantity_per_size)==0:
            quantity = get_total_quantity(production_order)
        else:
            quantity = get_total_quantity_from_shipment(doc)
        existing_details = get_product_details_from_order(production_order, "production")
        if quantity != 0 and existing_details!=None:
            if len(doc.shipment_quantity_per_size)==0:
                total_price = existing_details["old_value"] - calculate_price(get_size_from_prod_order(production_order))[production_order.product_name]
            else:
                total_price = existing_details["old_value"] - calculate_price(get_size_from_prod_shipment_order(doc,production_order.product_name))[production_order.product_name]
            final_quantity = existing_details["old_stock"]-quantity
            updateStock2(existing_details["stock_name"], final_quantity, existing_details["old_stock"], "Shipment Order", float(
                total_price)/final_quantity,"product",{"old":existing_details["size_details"],"new_incoming":get_shipment_qty_size_detail(doc)})



def get_total_quantity_from_shipment(order):
    # this functio returns total quantity of the order collecting all size quantities
    total_quantity = 0
    for size in order.shipment_quantity_per_size:
        if (size.quantity != None):
            total_quantity = total_quantity + int(size.quantity)
    return total_quantity

def get_shipment_qty_size_detail(doc):
    result_dic = {}
    for detail in doc.shipment_quantity_per_size:
        result_dic[detail.size] = detail.quantity
    return result_dic


def get_size_from_prod_order(order):
    # this returns a dictionary of size quantities with product name
    # output of this function can be used in calculate_price function
    size_order = {}
    size_order.update([(order.product_name, {})])
    for size in order.quantity_per_size:
        size_order[order.product_name].update(
            [(size.size, int(size.quantity))])
    return size_order

def get_size_from_prod_shipment_order(order,product_name):
    # this returns a dictionary of size quantities with product name
    # output of this function can be used in calculate_price function
    size_order = {}
    size_order.update([(product_name, {})])
    for size in order.shipment_quantity_per_size:
        size_order[product_name].update([(size.size, int(size.quantity))])
    return size_order

@frappe.whitelist()
def get_stock(item_type, ref):
    try:
        return frappe.get_all('Stock', filters={'item_type': item_type, 'internal_ref': ref}, fields=['quantity'])[0]
    except:
        return {'quantity': 0}

