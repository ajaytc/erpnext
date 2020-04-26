import frappe
import json



@frappe.whitelist()
def get_brand(user):
    return frappe.get_doc('User', user).brand_name


def signup(doc, method):
    
    if (doc.doctype=="Customer"):
        roles=[{"role": "Customer"}]
        email= doc.email_address
        first_name=doc.customer_name

    elif (doc.doctype=="Supplier"):
        email=doc.email
        first_name=doc.supplier_name
        if (doc.supplier_group=="Packaging"):
            roles=[{"role": "Packaging Vendor"}]
        elif (doc.supplier_group=="Fabric"):
            roles=[{"role": "Fabric Vendor"}]
        elif (doc.supplier_group=="Trimming"):
            roles=[{"role": "Trimming Vendor"}]
    elif (doc.doctype=="Production Factory"):
        roles=[{"role": "Manufacturing User"}]
        email= doc.email_address
        first_name=doc.factory_name
        

    

    user = frappe.get_doc({
        "doctype": "User",
        "enabled": 1,
        "new_password": doc.password,
        "user_type": "Website User",
        "email":email,
        "first_name":first_name,
        "roles":roles
    })
    

        
    user.flags.ignore_permissions = True
    user.flags.ignore_password_policy = True
    user.insert()
