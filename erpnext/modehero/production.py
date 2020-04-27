import frappe
import json
import ast
from erpnext.modehero.stock import updateStock2, get_details_fabric_from_order, get_details_trimming_from_order, get_product_details_from_order, get_details_packaging_from_order


@frappe.whitelist()
def create_production_order(data):
    data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    order = frappe.get_doc({
        'doctype': 'Production Order',
        'product_category': data['product_category'],
        'internal_ref': data['internal_ref'],
        'product_name': data['product_name'],
        'fabric_ref': data['fabric_ref'],
        'fabric_consumption': data['fabric_consumption'],
        'trimming': data['trimming_item'],
        'trimming_consumption': data['trimming_consumption'],
        'packaging': data['packaging_item'],
        'packaging_consumption': data['packaging_consumption'],
        'production_factory': data['production_factory'],
        'quantity_per_size': data['quantity'],
        'comment': data['comment'],
        'brand': brand
    })
    order.insert()

    order_quantities = get_order_quantities(order)
    # If there is a missvalue in any fabric/trimming/packaging consumption values, then no stock of all of three will not be reduced
    if order_quantities != None:
        existing_details = get_old_quantities_unitprice(order)
        if existing_details['fabric_details']:
            updateStock2(existing_details['fabric_details']['stock_name'],   existing_details['fabric_details']['old_stock']-order_quantities['fabric_quantity'],
                         existing_details['fabric_details']['old_stock'], "", existing_details['fabric_details']['unit_price'])
        if existing_details['trimming_details']:
            updateStock2(existing_details['trimming_details']['stock_name'], existing_details['trimming_details']['old_stock']-order_quantities['trimming_quantity'],
                         existing_details['trimming_details']['old_stock'], "", existing_details['trimming_details']['unit_price'])
        if existing_details['packaging_details']:
            updateStock2(existing_details['packaging_details']['stock_name'], existing_details['packaging_details']['old_stock']-order_quantities['packaging_quantity'],
                         existing_details['packaging_details']['old_stock'], "", existing_details['packaging_details']['unit_price'])
    return {'status': 'ok', 'order': order}


@frappe.whitelist()
def validate(order, isvalidate):
    order = frappe.get_doc('Production Order', order)
    if isvalidate == 'true':
        order.docstatus = 1
    else:
        order.docstatus = 1
        order.save()
        order.docstatus = 2
    order.save()
    frappe.db.commit()
    return order


@frappe.whitelist()
def set_finish(orderslist):
    orderslist = ast.literal_eval(orderslist)
    res_status = "ok"
    for order in orderslist:
        order = frappe.get_doc('Production Order', order)
        if (order):
            order.docstatus = 1
            order.save()
            order_quantity = get_total_quantity(order)
            if (order_quantity == None):
                continue
            existing_details = get_product_details_from_order(
                order, "production")
            if existing_details == None:
                continue

            size_order = get_size_order(order)
            price = calculate_price(size_order)[order.product_name] + existing_details['old_value']
            total_quantity = order_quantity+existing_details['old_stock']
            updateStock2(existing_details['stock_name'], total_quantity,
                         existing_details['old_stock'], "", price*1.0/total_quantity)
        else:
            res_status = "no"
    frappe.db.commit()
    return {'status': res_status}


@frappe.whitelist()
def submit_production_summary_info(data):
    data = json.loads(data)
    order = frappe.get_doc('Production Order', data['order'])
    order.expected_work_date = data['ex_work_date']
    order.confirmation_doc = data['confirmation_doc']
    order.profoma = data['profoma']
    order.invoice = data['invoice']
    order.carrier = data['carrier']
    order.tracking_number = data['tracking_number']
    order.shipment_date = data['shipment_date']
    order.production_comment = data['production_comment']
    order.save()
    return order


def get_total_quantity(order):
    # this functio returns total quantity of the order collecting all size quantities
    total_quantity = 0
    for size in order.quantity_per_size:
        if (size.quantity != None):
            total_quantity = total_quantity + int(size.quantity)
    return total_quantity


def get_order_quantities(order):
    # this function returns quantity details under fabric/trimming/packaging
    total_quantity = get_total_quantity(order)
    if (total_quantity == 0):
        return None
    try:
        fabric_quantity = total_quantity*int(order.fabric_consumption)
        trimming_quantity = total_quantity*int(order.trimming_consumption)
        packaging_quantity = total_quantity*int(order.packaging_consumption)
        return {'total_quantity': total_quantity, 'fabric_quantity': fabric_quantity, 'trimming_quantity': trimming_quantity, 'packaging_quantity': packaging_quantity}
    except:
        return None


def get_old_quantities_unitprice(order):
    # this function returns a dictionary of old quantity values and other details of fabric/trimming/packaging
    # data is gathered by functions in stock.py
    fabric_details = get_details_fabric_from_order(order)
    trimming_details = get_details_trimming_from_order(order, "production")
    packaging_details = get_details_packaging_from_order(order, "production")

    return {'fabric_details': fabric_details, 'trimming_details': trimming_details, 'packaging_details': packaging_details}


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


def get_size_order(order):
    # this returns a dictionary of size quantities with product name
    # output of this function can be used in calculate_price function
    size_order = {}
    size_order.update([(order.product_name, {})])
    for size in order.quantity_per_size:
        size_order[order.product_name].update(
            [(size.size, int(size.quantity))])
    return size_order
