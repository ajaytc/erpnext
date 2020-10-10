import frappe
import json
import ast


@frappe.whitelist()
def create_factory(data):
    data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    factory = frappe.get_doc({
        'doctype': 'Production Factory',
        'brand': brand,
        'email_address': data['email'],
        'address_line_1': data['address1'],
        'address_line_2': data['address2'],
        'contact': data['contact'],
        'phone': data['phone_number'],
        'city_town': data['city'],
        'zip_code': data['zip_code'],
        'factory_name': data['name']
    })
    factory.insert()
    frappe.db.commit()
    return {'status': 'ok', 'factory': factory}

def add_brand_factory(doc,method):
    child_dic = {
                    "factory":doc.name,
                    "brand": doc.brand
                }
    doc.append("assigned_brands",child_dic)
    doc.save()
    frappe.db.commit()

@frappe.whitelist()
def get_official_factories():
    try:
        suppliers = frappe.get_all('Production Factory', filters={'is_official': 1}, fields=['name','factory_name'])
        result = []
        for x in suppliers:
            result.append({
                'label': x.factory_name,
                'value': x.factory_name
            })
        return result
    except:
        return []

@frappe.whitelist()
def get_official_factory_data(factory_name):
    official_facs = frappe.get_all("Production Factory",{"factory_name":factory_name,"is_official":1},["factory_name","contact","email_address","address_line_1","address_line_2","phone","city_town","country","zip_code"])
    if len(official_facs)==0:
        return {"status":"error"}
    return {"status":"ok","data":official_facs[0]}