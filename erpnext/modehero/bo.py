import ast
import json
import frappe
import datetime


@frappe.whitelist()
def get_excel_of_brands():
    lists = []
    excel_string = ""
    headers = ['','','',"Address",'','','',"Subscription",'','','']
    columns = ["Brand Name","Inscription Date","Email","Street","City","Zip","Country","Start","End","Plan","Billed"]
    lists = [headers,columns]
    brands = frappe.get_all("Company",["name","creation","email","subscription_period","subscribed_date","subscription_end_date","subscribed_plan"])
    for brand in brands:
        if brand["email"]==None:
            continue
        user = frappe.get_all("User",{"name":brand["email"]},["city","zip_code","country"])
        if len(user)==0:
            continue
        temp = [brand["name"],brand["creation"].strftime('%Y-%m-%d'),brand["email"],"",user[0]["city"],user[0]["zip_code"],user[0]["country"],brand["subscribed_date"],brand["subscription_end_date"]]
        if brand["subscribed_plan"]!=None:
            plan =frappe.get_all("Payment Plan",{"name":brand["subscribed_plan"]},["plan_name"])
            if len(plan)==0:
                temp.append('')
            else:
                temp.append(plan[0]["plan_name"])
        else:
            temp.append('')
        temp.append(brand["subscription_period"])
        lists.append(temp)
    for list1 in lists:
        excel_string = excel_string + collect_list_as_string_commas(list1)+"\n"
    return {"status":"ok","stream":excel_string}

@frappe.whitelist()
def make_official(official_wanted):
    official_wanted = ast.literal_eval(official_wanted)
    is_completed = True
    for snf in official_wanted:
        try:  
            if snf["type"]=="Factory":  
                set_official("Production Factory",snf["name"])
            else:
                set_official("Supplier",snf["name"])
        except Exception:
            is_completed = False
    frappe.db.commit()
    if is_completed:
        return {"status":"ok"}
    else:
        return {"status":"error"}

@frappe.whitelist()
def add_subscription_to_snf(dates,snf_type,snf_name):
    dates = json.loads(dates)
    start_date = dates["start_date"]
    end_date = dates["end_date"]
    if snf_name=="" or snf_name==None or snf_type=="" or snf_type==None or  not(is_date(end_date)) or not(is_date(start_date)):
        return {"status":"error"}
    elif not compare_dates(start_date,end_date):
        return {"status":"error"}
    is_completed = True
    if snf_type=="Factory":
        doctype = "Factory"
    else:
        doctype = "Supplier"
    try:
        add_snf_subscription(start_date,end_date,snf_name,doctype)
        frappe.db.commit()
    except Exception:
        is_completed = False
    if not is_completed:
        return {"status":"error"}
    return {"status":"ok"}

def compare_dates(first , second):
    try:
        if datetime.datetime.strptime(first, '%Y-%m-%d')>datetime.datetime.strptime(second, '%Y-%m-%d'):
            return False
    except Exception:
        print ("=====>Date Format Error<=====")
        return False
    return True

def collect_list_as_string_commas(list1):
    temp = ""
    for x in range(len(list1)):
        k = list1[x]
        if k==None : k=''
        elif isinstance(k, datetime.date):
            k = k.strftime('%Y-%m-%d')
        if x==len(list1)-1:
            temp = temp+ k
            break
        temp = temp+ k + ","
    return temp

def set_official(doctype,name):
    frappe.db.set_value(doctype, name, {
        'is_official': 1
    })

def is_date(date_str):
    try:
        datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return False
    return True

def add_snf_subscription(start_date,end_date,snf_name,doctype):
    frappe.db.set_value(doctype, snf_name, {
        'subscribed_date': start_date,
        'subscription_end_date':end_date,
        'is_official': 1
    })