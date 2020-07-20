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
def set_pricing(form_data):
    form_data = json.loads(form_data)
    # here the consisency of the from to values are checked.
    # wholesale_prices = check_wholesale_correct(form_data["wholesale_price"])
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    pricing = form_data["client"] + " " + form_data["season"]
    pricing = frappe.get_doc(
        {
            "doctype": "Client Pricing",
            "brand": brand,
            "client": form_data["client"],
            "item_group": form_data["item_group"],
            "item_code": form_data["item_code"],
            "season": form_data["season"],
            "minimum_order": form_data["minimum_order"],
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
    