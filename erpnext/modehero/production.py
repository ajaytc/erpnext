import frappe
import json
import ast
from erpnext.modehero.stock import updateStock2, get_details_fabric_from_order, get_details_trimming_from_order, get_product_details_from_order, get_details_packaging_from_order


@frappe.whitelist()
def create_production_order(data):

# data:{
# 'product_category':'proto - Moynat'
# 'internal_ref':'xsc'
# 'product_name':'29'
# 'production_factory':'facto 2'
# 'quantity':[{'quantity': '4', 'size': 'A'}]
# 'fab_suppliers':{'0.485899247691032': {'fabric_con': '23', 'fabric_ref': '464864', 'fabric_status': 'To be sent later', 'fabric_supplier': 'Loro Piana'}, '0.8194292281842649': {'fabric_con': '23', 'fabric_ref': '223311', 'fabric_status': None, 'fabric_supplier': 'TEST RED'}}
# 'trim_suppliers':{'0.15179674763375983': {'trim_con': '22', 'trim_ref': 'wed', 'trim_status': 'On stock at factory', 'trim_supplier': 'dtrim'}}
# 'pack_suppliers':{'0.4848414809400162': {'pack_con': '34', 'pack_ref': 'PB 20', 'pack_status': 'To be sent later', 'pack_supplier': 'Packager1'}, '0.6865090500983441': {'pack_con': '31', 'pack_ref': 'adsf', 'pack_status': 'To be sent later', 'pack_supplier': 'Packager1'}, '0.9813391020556028': {'pack_con': '34', 'pack_ref': 'qqq', 'pack_status': 'To be sent later', 'pack_supplier': 'Packager1'}}
# 'comment':''
# }

    data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name

    json_fab_suppliers = data['fab_suppliers']
    json_trim_suppliers = data['trim_suppliers']
    json_pack_suppliers = data['pack_suppliers']

    fab_refs = []
    trim_refs = []
    pack_refs = []

    order_suppliers = []

    for key in json_fab_suppliers:
        if(json_fab_suppliers[key] != {}):
            if(json_fab_suppliers[key]['fabric_ref'] != None):
                fab_refs.append(json_fab_suppliers[key]['fabric_ref'])
                order_suppliers.append({
                    'supplier': json_fab_suppliers[key]['fabric_supplier'],
                    'supplier_group': 'Fabric',
                    'fabric_consumption': json_fab_suppliers[key]['fabric_con'],
                    'fabric_ref': json_fab_suppliers[key]['fabric_ref'],
                    'fabric_status': json_fab_suppliers[key]['fabric_status']
                })

    for key in json_trim_suppliers:
        if(json_trim_suppliers[key] != {}):
            if(json_trim_suppliers[key]['trim_ref'] != None):
                trim_refs.append(json_trim_suppliers[key]['trim_ref'])
                order_suppliers.append({
                    'supplier': json_trim_suppliers[key]['trim_supplier'],
                    'supplier_group': 'Trimming',
                    'trimming_consumption': json_trim_suppliers[key]['trim_con'],
                    'trimming_ref': json_trim_suppliers[key]['trim_ref'],
                    'trimming_status': json_trim_suppliers[key]['trim_status']

                })

    for key in json_pack_suppliers:
        if(json_pack_suppliers[key] != {}):
            if(json_pack_suppliers[key]['pack_ref'] != None):
                pack_refs.append(json_pack_suppliers[key]['pack_ref'])
                order_suppliers.append({
                    'supplier': json_pack_suppliers[key]['pack_supplier'],
                    'supplier_group': 'Packaging',
                    'packaging_consumption': json_pack_suppliers[key]['pack_con'],
                    'packaging_ref': json_pack_suppliers[key]['pack_ref'],
                    'packaging_status': json_pack_suppliers[key]['pack_status']
                })

    order = frappe.get_doc({
        'doctype': 'Production Order',
        'product_category': data['product_category'],
        'internal_ref': data['internal_ref'],
        'product_name': data['product_name'],
        'production_factory': data['production_factory'],
        'final_destination':data['final_destination'],
        'quantity_per_size': data['quantity'],
        'suppliers': order_suppliers,
        'comment': data['comment'],
        'brand': brand
    })
    order.insert(ignore_permissions=True)

    order_quantities = get_order_quantities(order)
    # If there is a missvalue in any fabric/trimming/packaging consumption values, then no stock of all of three will not be reduced
    if order_quantities != None:
        try:
            existing_details = get_old_quantities_unitprice(
            order_quantities['fabric_quantities'], order_quantities['trimming_quantities'], order_quantities['packaging_quantities'])
            if existing_details['fabric_details']:
                for fabric_detail in existing_details['fabric_details']:
                    updateStock2(fabric_detail['stock_name'], fabric_detail['old_stock']-fabric_detail['fab_quantity'],
                                fabric_detail['old_stock'], "Production Fabric", fabric_detail['unit_price'])

            if existing_details['trimming_details']:
                for trimming_detail in existing_details['trimming_details']:
                        updateStock2(trimming_detail['stock_name'], trimming_detail['old_stock']-trimming_detail['trim_quantity'],
                                    trimming_detail['old_stock'], "Production Trimming", trimming_detail['unit_price'])
            if existing_details['packaging_details']:
                for packaging_detail in existing_details['packaging_details']:
                    updateStock2(packaging_detail['stock_name'], packaging_detail['old_stock']-packaging_detail['pack_quantity'],
                                packaging_detail['old_stock'], "Production Packaging", packaging_detail['unit_price'])

        except :
            print("Stocks not updated")
       

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
    order.save(ignore_permissions=True)
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
            stockUpdateAfterFinish(order)
        else:
            res_status = "no"
    frappe.db.commit()
    return {'status': res_status}


def stockUpdateAfterFinish(order):
    order_quantity = get_total_quantity(order)
    if (order_quantity == None):
        return
    existing_details = get_product_details_from_order(
        order, "production")
    if existing_details == None:
        return

    size_order = get_size_order(order)
    price = calculate_price(size_order)[
        order.product_name] + existing_details['old_value']
    total_quantity = int(order_quantity)+existing_details['old_stock']
    updateStock2(existing_details['stock_name'], total_quantity,
                 existing_details['old_stock'], "Production", price*1.0/total_quantity)


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
    if(order.profoma != 'None'):
        order.docstatus = 1
    order.save()
    if(order.invoice != 'None'):
        stockUpdateAfterFinish(order)
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
    fabric_quantities = []
    trimming_quantities = []
    packaging_quantities = []
    if (total_quantity == 0):
        return None
    try:
        for supplier in order.suppliers:
            if(supplier.supplier_group == 'Fabric'):
                fabric_quantity={}
                fabric_quantity['supplier'] = supplier.supplier
                fabric_quantity['fabric_ref'] = supplier.fabric_ref
                fabric_quantity['quantity'] = total_quantity*int(supplier.fabric_consumption)

                fabric_quantities.append(fabric_quantity)
            elif(supplier.supplier_group == 'Trimming'):
                trimming_quantity={}
                trimming_quantity['supplier'] = supplier.supplier
                trimming_quantity['trimming_ref'] = supplier.trimming_ref
                trimming_quantity['quantity'] =total_quantity*int(supplier.trimming_consumption)
                trimming_quantities.append(trimming_quantity)
            elif(supplier.supplier_group == 'Packaging'):
                packaging_quantity={}
                packaging_quantity['supplier'] = supplier.supplier
                packaging_quantity['packaging_ref'] = supplier.packaging_ref
                packaging_quantity['quantity'] = total_quantity*int(supplier.packaging_consumption)
                packaging_quantities.append(packaging_quantity)
              

        return {'total_quantity': total_quantity, 'fabric_quantities': fabric_quantities, 'trimming_quantities': trimming_quantities, 'packaging_quantities': packaging_quantities}
    except:
        return None


def get_old_quantities_unitprice(fabric_quantities, trimming_quantities,packaging_quantities):
    # this function returns a dictionary of old quantity values and other details of fabric/trimming/packaging
    # data is gathered by functions in stock.py
    fabric_details = []
    trimming_details = []
    packaging_details = []

    for fab_quantity in fabric_quantities:
        order =frappe.get_doc({
            'doctype':'Item Supplier',
            'fabric_ref': fab_quantity['fabric_ref']
        })
        fabric_detail = get_details_fabric_from_order(order)
        fabric_detail['fab_quantity']=fab_quantity['quantity']
        fabric_details.append(fabric_detail)

    for trim_quantity in trimming_quantities:
        order =frappe.get_doc({
            'doctype':'Item Supplier',
            'trimming_ref': trim_quantity['trimming_ref']
        })
       
        trimming_detail = get_details_trimming_from_order(order, "production")
        trimming_detail['trim_quantity']=trim_quantity['quantity']
        trimming_details.append(trimming_detail)

    for pack_quantity in packaging_quantities:
        order =frappe.get_doc({
            'doctype':'Item Supplier',
            'packaging_ref': pack_quantity['packaging_ref']
        })
        packaging_detail = get_details_packaging_from_order(order, "production")
        if(packaging_detail== None):
            return None
        packaging_detail['pack_quantity']=pack_quantity['quantity']
        packaging_details.append(packaging_detail)

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


@frappe.whitelist()
def submitPaymentProof(data):
    data = json.loads(data)
    orderName=data['order']
    order=frappe.get_doc("Production Order",orderName)

    order.payment_proof=data['payment_proof']
    order.save()
    return order