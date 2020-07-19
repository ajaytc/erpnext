import frappe
import json


@frappe.whitelist()
def get_products_of_category(category):
    return frappe.get_list('Item', filters={'item_group': category}, fields=['name', 'item_name'])


@frappe.whitelist()
def get_item_code():
    items = frappe.get_all(
        'Item', order_by='creation desc', fields=['item_code'])
    return int(items[0].item_code)+1


@frappe.whitelist()
def create_product_category(data):
    data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    item = frappe.get_doc({
        'doctype': 'Item Group',
        'brand_name': brand,
        'item_group_name': data['name'],
    })
    item.insert()
    frappe.db.commit()
    return {'status': 'ok', 'item': item}


@frappe.whitelist()
def create_garmentlabel(data):
    data = json.loads(data)
    item = frappe.get_doc({
        'doctype': 'Garment Label',
        'customer': brand,
        'label_name': data['label_name'],
        'label': data['label'],
    })
    item.insert()
    frappe.db.commit()
    return {'status': 'ok', 'item': item}


@frappe.whitelist()
def create_product_item(data):
    data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name

    json_prices = data['prices']
    json_fab_suppliers = data['fab_suppliers']
    json_trim_suppliers = data['trim_suppliers']
    json_pack_suppliers = data['pack_suppliers']
    prices = []
    item_suppliers = []

    for key in json_prices:
        prices.append({
            'from': json_prices[key]['from'],
            'to': json_prices[key]['to'],
            'price': json_prices[key]['price']
        })

    for key in json_fab_suppliers:
        if(json_fab_suppliers[key] != {}):
            if(json_fab_suppliers[key]['fabric_ref'] != None):
                item_suppliers.append({
                    'supplier': json_fab_suppliers[key]['fabric_supplier'],
                    'supplier_group': 'Fabric',
                    'fabric_consumption': json_fab_suppliers[key]['fabric_con'],
                    'fabric_ref': json_fab_suppliers[key]['fabric_ref']
                })

    for key in json_trim_suppliers:
        if(json_trim_suppliers[key] != {}):
            if(json_trim_suppliers[key]['trim_ref'] != None):
                item_suppliers.append({
                    'supplier': json_trim_suppliers[key]['trim_supplier'],
                    'supplier_group': 'Trimming',
                    'trimming_consumption': json_trim_suppliers[key]['trim_con'],
                    'trimming_ref': json_trim_suppliers[key]['trim_ref']

                })

    for key in json_pack_suppliers:
        if(json_pack_suppliers[key] != {}):
            if(json_pack_suppliers[key]['pack_ref'] != None):
                item_suppliers.append({
                    'supplier': json_pack_suppliers[key]['pack_supplier'],
                    'supplier_group': 'Packaging',
                    'packaging_consumption': json_pack_suppliers[key]['pack_con'],
                    'packaging_ref': json_pack_suppliers[key]['pack_ref']
                })

    tech_pack = ""
    picture = ""
    pattern = ""
    barcode = ""
    avg_price=0


    if("tech_pack" in data):
        tech_pack = data['tech_pack']
    else:
        tech_pack = None
    if('picture' in data):
        picture = data['picture']
    else:
        picture = None
    if('pattern' in data):
        pattern = data['pattern']
    else:
        pattern = None
    if('barcode' in data):
        barcode = data['barcode']
    else:
        barcode = None
    if(data['avg_price']==''):
        avg_price=0
    else:
        avg_price=data['avg_price']
    if(prices==[]):
        prices=None

    if(data['item_name'] == None):
        if(data['item_group'] == None):
            return {'message': 'Product name and Product Category not filled'}
        else:
            return {'message': 'Product name not filled'}
    elif(data['item_group'] == None):
        return {'message': 'Product Category not filled'}
    else:

        product = frappe.get_doc({
            'doctype': 'Item',
            'item_code':get_item_code(),
            'item_name': data['item_name'],
            'item_group': data['item_group'],
            'sizing': data['sizing'],
            'avg_price':avg_price,
            'production_price': prices,
            'supplier': item_suppliers,
            'tech_pack': tech_pack,
            'picture': picture,
            'pattern': pattern,
            'barcode': barcode

        })
        product.insert()
        frappe.db.commit()
        return {'message': 'Product Created Successfully', 'product': product}
    print(data)

@frappe.whitelist()
def get_priducts_of_category(category):
    brand = frappe.get_doc('User', frappe.session.user).brand_name
    result = frappe.get_all('Item',filters={'item_group':category,'brand':brand},fields=['item_name','name'])
    return result

@frappe.whitelist()
def get_product_item(product):
    product=frappe.get_doc('Item',product)
    return product
