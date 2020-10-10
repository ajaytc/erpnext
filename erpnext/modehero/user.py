import frappe
import json
import random
import string
from datetime import date, datetime


@frappe.whitelist()
def get_brand(user):
    return frappe.get_doc('User', user).brand_name



def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
    # print("Random string of length", length, "is:", result_str)

def signup(doc, method):

    if (doc.doctype == "Customer"):
        roles = [{"role": "Customer"}]
        user_type='client'
        email = doc.email_address
        first_name = doc.customer_name

    elif (doc.doctype == "Supplier"):
        email = doc.email
        first_name = doc.supplier_name
        if (doc.supplier_group == "Packaging"):
            roles = [{"role": "Packaging Vendor"}]
            user_type='packaging_supplier'
        elif (doc.supplier_group == "Fabric"):
            roles = [{"role": "Fabric Vendor"}]
            user_type='fabric_supplier'
        elif (doc.supplier_group == "Trimming"):
            roles = [{"role": "Trimming Vendor"}]
            user_type='trimming_supplier'
    elif (doc.doctype == "Production Factory"):
        roles = [{"role": "Manufacturing User"}]
        user_type='factory'
        email = doc.email_address
        first_name = doc.factory_name

    brandName=getBrandName()

    user = frappe.get_doc({
        "doctype": "User",
        "enabled": 1,
        "new_password": get_random_string(12),
        "user_type": "Website User",
        "email": email,
        "type":user_type,
        "brand_name":brandName,
        "first_name": first_name,
        "roles": roles
    })

    user.flags.ignore_permissions = True
    user.flags.ignore_password_policy = True
    user.insert()

def getBrandName():
    roles=frappe.get_roles(frappe.session.user)
    if('Administrator' in roles):
        brandName=None
    else:
        brandName=frappe.get_doc("User",frappe.session.user).brand_name
    
    return brandName

def auto_deactivate():
    print('running user deactivation cron')
    users = frappe.get_all('User')
    dateformat = '%d-%m-%Y'
    for u in users:
        user = frappe.get_doc('User', u)
        if user.paid == '0':
            delta = datetime.now() - datetime.strptime(frappe.format(user.creation, 'Date'), dateformat)
            if delta.days > 14:
                user.enabled = 0
                user.save()
                print('disable user', user.name)
    return {'status': 'ok'}

@frappe.whitelist()
def auto_deactivate_brands():
    print('running brands deactivation cron')
    brands = frappe.get_all('Company')
    dateformat = '%d/%m/%Y'
    for brand_name in brands:
        brand = frappe.get_doc('Company', brand_name)
        if(inTrialPeriod(brand)):
            continue
        else:
            if(brand.enabled == 1):
                if(brand.subscription_end_date!=None):
                    if(datetime.strptime(frappe.format(brand.subscription_end_date, 'Date'), dateformat)<= datetime.now()):
                        brand.enabled = 0
                        brand.save()
                        print('disable user', brand.name)
                else:
                    brand.enabled = 0
                    brand.save()
                    print('disable user', brand.name)
    return {'status': 'ok'}

@frappe.whitelist()
def auto_deactivate_snf():
    print('running snf deactivation cron')
    suppliers = frappe.get_all('Suppplier')
    factories = frappe.get_all('Production Factory')
    deactive_factories(factories)
    deactive_suppliers(suppliers)
    return {'status': 'ok'}

def deactive_factories(factories):
    dateformat = '%d/%m/%Y'
    for factory_name in factories:
        factory = frappe.get_doc('Production Factory', factory_name)
        if(inTrialPeriod(factory)):
            continue
        else:
            if(factory.enabled == 1):
                if(factory.subscription_end_date!=None):
                    if(datetime.strptime(frappe.format(factory.subscription_end_date, 'Date'), dateformat)<= datetime.now()):
                        factory.enabled = 0
                        factory.save()
                        print('disable user', factory.name)
                else:
                    factory.enabled = 0
                    factory.save()
                    print('disable user', factory.name)

def deactive_suppliers(suppliers):
    dateformat = '%d/%m/%Y'
    for supplier_name in suppliers:
        supplier = frappe.get_doc('Supplier', supplier_name)
        if(inTrialPeriod(supplier)):
            continue
        else:
            if(supplier.enabled == 1):
                if(supplier.subscription_end_date!=None):
                    if(datetime.strptime(frappe.format(supplier.subscription_end_date, 'Date'), dateformat)<= datetime.now()):
                        supplier.enabled = 0
                        supplier.save()
                        print('disable user', supplier.name)
                else:
                    supplier.enabled = 0
                    supplier.save()
                    print('disable user', supplier.name)

def inTrialPeriod(doc):
    dateformat = '%d/%m/%Y'
    spent_duration=datetime.now() - datetime.strptime(frappe.format(doc.creation, 'Date'), dateformat)
    trial_period=frappe.get_all("System Data",filters={'type':'brand-trial-period'},fields=['value'])
    if(spent_duration.days<=int(trial_period[0]['value'])):
        return True
    else:
        return False


@frappe.whitelist()
def test_deactivate():
    return auto_deactivate()


def haveAccess(module):
    brandName=frappe.get_doc('User', frappe.session.user).brand_name
    brand=frappe.get_doc("Company",brandName)
    # subscribedPlan=frappe.get_doc("Payment Plan",brand.subscribed_plan)

    brandDict=brand.__dict__
    if(brand.enabled==1):
        if(inTrialPeriod(brand)):
            return True
        else:
            if(brandDict[module]==1):
                return True
            else:
                return False
    else:
        return False

def haveAccessForSupplier(module):
    suppliers = frappe.get_all("Supplier",{"email":frappe.session.user})
    if len(suppliers)!=1:
        return False
    supplier=frappe.get_doc("Supplier",suppliers[0]["name"])
    supplierDict=supplier.__dict__
    if(inTrialPeriod(supplier)):
        return True
    elif(supplier.enabled==1):
        return True
    else:
        return False

def haveAccessForFactory(module):
    factories = frappe.get_all("Production Factory",{"email":frappe.session.user})
    if len(suppliers)!=1:
        return False
    factory=frappe.get_doc("Production Factory",factories[0]["name"])
    factoryDict=factory.__dict__
    if(inTrialPeriod(factory)):
        return True
    elif(factory.enabled==1):
        return True
    else:
        return False
    

def getAccessList():
    # brandName=frappe.get_doc('User', frappe.session.user).brand_name
    if(frappe.get_doc('User', frappe.session.user).type=='brand' or frappe.get_doc('User', frappe.session.user).type=='Administrator' ):
        modules=['client','supply','pre_production','production','shipment','stock','snf']
        brandName=frappe.get_doc('User', frappe.session.user).brand_name
        brand=frappe.get_doc("Company",brandName)
        # subscribedPlan=frappe.get_doc("Payment Plan",brand.subscribed_plan)
        brandDict=brand.__dict__
        accessingModules=[]

        if(inTrialPeriod(brand)):
            accessingModules=modules
        else:
            for mod in modules:
                if(brandDict[mod]==1):
                    accessingModules.append(mod)

        return accessingModules


