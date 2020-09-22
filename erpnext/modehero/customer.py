import frappe
import json
import ast


@frappe.whitelist()
def get_customer(email):
    try:
        return frappe.get_all('Customer', filters={'email_address': email})[0].name
    except:
        frappe.throw(frappe._("Error"))

@frappe.whitelist()
def get_branded_companies():
    brand = frappe.get_doc('User', frappe.session.user).brand_name
    company_objs = frappe.get_all('Customer',filters={'brand':brand},fields=['name'])
    result = []
    for x in company_objs:
        result.append({
            'label':x.name,
            'value':x.name
        })
    return result
@frappe.whitelist()
def modify_pricing(form_data,name):
    form_data = json.loads(form_data)
    try:
        for wp_dic in form_data["wholesale_price"]:
            for key in wp_dic : 
                if key=="price" : wp_dic[key]=float(wp_dic[key]) 
                else : wp_dic[key]=int(wp_dic[key]) 
        for op in form_data["pricing_options"]:
            op["price"] = float(op["price"])
    except ValueError:
        return {'status': 'error'}
    # here the consisency of the from to values are checked.
    # wholesale_prices = check_wholesale_correct(form_data["wholesale_price"])
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    pricing = form_data["client"] + " " + form_data["season"]
    try:
        pricing = {
                "season": form_data["season"],
                "minimum_order": int(form_data["minimum_order"]),
                "show_price": form_data["show_price"],
                "pricing_name":pricing
            }
        ap = frappe.get_doc('Client Pricing', name)
        ap.wholesale_price = []
        ap.pricing_options = []
        ap = update_wholesales(ap,form_data["wholesale_price"])
        ap = modify_options(ap,form_data["pricing_options"])
        for field in pricing:
            setattr(ap, field, pricing[field])
    except ValueError:
        return {"status":"error"}
    ap.save(ignore_permissions=True)
    frappe.db.commit()
    return {'status': 'ok'}

def update_wholesales(doc,new_wp_dic):

    doc_list = []
    for wp in new_wp_dic:
        wh_price = {
            "parentfield":"wholesale_price",
            "from_quantity": int(wp["from_quantity"]),
            "to_quantity": int(wp["to_quantity"]),
            "price": wp["price"]
         }
        doc.append("wholesale_price",wh_price)
    return doc

def modify_options(doc,new_opt_dic):

    for op in new_opt_dic:
        op_price ={
            "parentfield":"pricing_options",
            "option": op["option"],
            "price": op["price"]
        }
        doc.append("pricing_options",op_price)
    return doc

    
def make_delete_option_query(options):
    option_query = '''DELETE FROM `tabPricing Options` WHERE name IN ("'''
    for option in range(len(options)):
        if (option==len(options)-1):
            option_query = option_query + options[option].name+'")'
        else:
            option_query = option_query + options[option].name+'","'
    return option_query
def make_delete_wp_query(wps):
    wp_query = '''DELETE FROM `tabWholesale Price` WHERE name IN ("'''
    for wp in range(len(wps)):
        if (wp==len(wps)-1):
            wp_query = wp_query + wps[wp].name+'")'
        else:
            wp_query = wp_query + wps[wp].name+'","'
    return wp_query

@frappe.whitelist()
def set_pricing(form_data):
    form_data = json.loads(form_data)
    if ((not type(form_data["wholesale_price"]) is list) or (not type(form_data["pricing_options"]) is list)  or len(form_data["client"].strip())==0 or len(form_data["item_code"].strip())==0 or len(form_data["item_group"].strip())==0 or len(form_data["season"].strip())==0 or (not is_number( str(form_data["minimum_order"]))) ):
        return {'status': 'error'}
    elif (len(form_data["wholesale_price"])==0):
        return {'status': 'error'}
    # here the consisency of the from to values are checked.
    try:
        for wp_dic in form_data["wholesale_price"]:
            for key in wp_dic : 
                if key=="price" : wp_dic[key]=float(wp_dic[key]) 
                else : wp_dic[key]=int(wp_dic[key]) 
        for op in form_data["pricing_options"]:
            op["price"] = float(op["price"])
    except ValueError:
        return {'status': 'error'}
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    already_set = is_already_set(form_data["client"],form_data["item_code"],brand)
    if (already_set):
        return {'status': 'error'}
    pricing = form_data["client"] + " " + form_data["season"]
    pricing = frappe.get_doc(
        {
            "doctype": "Client Pricing",
            "brand": brand,
            "client": form_data["client"],
            "item_group": form_data["item_group"],
            "item_code": form_data["item_code"],
            "season": form_data["season"],
            "minimum_order": int(form_data["minimum_order"]),
            "show_price": form_data["show_price"],
            "wholesale_price":form_data["wholesale_price"],
            "pricing_options":form_data["pricing_options"],
            "pricing_name":pricing
         })

    pricing.insert(ignore_permissions=True)
    frappe.db.commit()
    return {'status': 'ok'}


# def check_wholesale_correct(wholesale_dicts):
#     is_any_wrong = False
#     temp_num_checker = []
#     wholesale_dicts.sort(key=get_from)
#     for dic in wholesale_dicts:
#         if (len(temp_num_checker)==0):
#             temp_num_checker.append(dic["from"])
#             temp_num_checker.append(dic["to"])
#             continue
#         length_temp = len(temp_num_checker)
#         if (temp_num_checker[length_temp-2]>temp_num_checker[length_temp-1] | dic["from"]!=temp_num_checker[length_temp-1]+1 ):
#             is_any_wrong = True
#             break
#     if (is_any_wrong):
#         return False
#     return True

# def get_from(wholesale_dict):
#     return wholesale_dict['from']

def is_already_set(client,item_code,brand):
    existing_data = frappe.get_all('Client Pricing',filters={'client':client,'item_code':item_code,'brand':brand})
    if len(existing_data)==0:
        return False
    return True


def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

@frappe.whitelist()
def deactivate_pricing(name_list):
    name_list = ast.literal_eval(name_list)
    for name in name_list:
        ap = frappe.get_doc('Client Pricing',name)
        ap.docstatus = 1
        ap.save(ignore_permissions=True)
    frappe.db.commit()
    return {'status': 'ok'}