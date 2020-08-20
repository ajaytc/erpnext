import frappe
import json
import ast

@frappe.whitelist()
def get_pos_of_client(client):
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    pos_list=frappe.get_all("Point Of Sales",filters={'parent_company':client,'brand':brand},fields=['point_of_sale','name'])
    return pos_list

@frappe.whitelist()
def get_packages_of_client(client):
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    package_list=frappe.get_all("Package",filters={'client':client,'brand':brand},fields=['package_name','name'])
    return package_list

@frappe.whitelist()
def get_products_of_package(packageName):
    package=frappe.get_doc("Package",packageName)
    productQtys=package.package_quantity
    productDetails=[]

    for product in productQtys:
        productName=product.item_code
        productOb=frappe.get_doc('Item',productName)
        prod={
            'prod_name':productOb.item_name,
            'qty':product.quantity
        };
        productDetails.append(prod)


    return productDetails