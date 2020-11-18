from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime
import base64
import os
from frappe.utils.pdf import getBase64Img, getImagePath

no_cache = 1


def get_context(context):
    fabSuppliers = []
    trimSuppliers = []
    packSuppliers = []
    params = frappe.form_dict

    if('order' in params):
        context.order = frappe.get_doc('Production Order', params.order)

    user = frappe.get_doc('User', frappe.session.user)

    context.product = frappe.get_doc('Item', context.order.product_name)

    getSuppliers(context.order, fabSuppliers, trimSuppliers, packSuppliers)
    # brand_name = frappe.get_doc('User', frappe.session.user).brand_name
    brand_name = context.product.brand

    brand = frappe.get_all("User", filters={"type": "brand", "brand_name": brand_name}, fields=[
        "user_image", "address1", "name"])

    context.brand_logo = getBrandLogo(brand[0].user_image)

    context.address = brand[0].address1

    temp = frappe.get_all("Pdf Document", filters={"type": "Bulk Order"}, fields=[
        "content", "type", "name"])

    context.order_name = params.order

    context.fabricSuppliers = fabSuppliers
    context.trimmingSuppliers = trimSuppliers
    context.packagingSuppliers = packSuppliers

    t = frappe.render_template(temp[0]['content'], context)
    context.template = t

    context.roles = frappe.get_roles(frappe.session.user)
    context.isCustomer = "Customer" in context.roles
    context.isBrand = "Brand User" in context.roles
    context.isProd = "Manufacturing User" in context.roles
    if frappe.session.user == 'Guest':
        context.isGuest=True
    else:
        context.isGuest=False

    context.destination = getDestination(context)

    if('sk' in params):
        context.isProd=True
    else:
        context.isProd = "Manufacturing User" in context.roles

# context.parents = [
#     {"name": frappe._("Home"), "route": "/"}
# ]

    return context


def getDestination(context):
    if (frappe.db.exists("Destination", context.order.final_destination) != None):
        destination=frappe.get_doc("Destination", context.order.final_destination).destination_name
    elif (frappe.db.exists("Point Of Sales", context.order.final_destination) !=None):
        destination=frappe.get_doc("Point Of Sales", context.order.final_destination).point_of_sale
    else:
        destination=None
    
    return destination


def getSuppliers(order, fabSuppliers, trimSuppliers, packSuppliers):

    suppliers=order.suppliers

    for supplier in suppliers:
        if(supplier.supplier_group == 'Fabric'):
            if(supplier.fabric_ref != ''):

                fabric=frappe.get_doc("Fabric", supplier.fabric_ref)

                fabSupplierOb={}
                if(fabric.fabric_image != None):
                    fabSupplierOb["fabric_pic"]=getBase64Img(
                        fabric.fabric_image)

                    # my_string=my_string.split("'")[1]
                else:
                    fabSupplierOb["fabric_pic"]=''

                fabSupplierOb["supplier"]=supplier.supplier
                fabSupplierOb["fabric_ref"]=supplier.fabric_ref
                fabSupplierOb["fabric_consumption"]=supplier.fabric_consumption
                fabSupplierOb["fabric_status"]=supplier.fabric_status

                fabSupplierOb["color"] = frappe.get_doc("Color", fabric.color).color_name
                fabSupplierOb["width"] = frappe.get_doc("Width", fabric.width).width
                fabSupplierOb["fabric_way"]=fabric.fabric_way
                fabSuppliers.append(fabSupplierOb)
        elif (supplier.supplier_group == 'Trimming'):
            if(supplier.trimming_ref != ''):
                trim=frappe.get_doc("Trimming Item", supplier.trimming_ref)

                trimOb={}
                if(trim.trimming_image != None):
                    trimOb["trim_pic"]=getBase64Img(trim.trimming_image)

                    # my_string=my_string.split("'")[1]
                else:
                    trimOb["trim_pic"]=''

                trimOb["supplier"]=supplier.supplier
                trimOb["trimming_ref"]=supplier.trimming_ref
                trimOb["trimming_consumption"]=supplier.trimming_consumption
                trimOb["trimming_status"]=supplier.trimming_status

                trimOb["color"] = frappe.get_doc("Color", trim.color).color_name
                trimOb["size"]=trim.trimming_size

                trimSuppliers.append(trimOb)
        elif (supplier.supplier_group == 'Packaging'):
            if(supplier.packaging_ref != ''):
                pack=frappe.get_doc("Packaging Item", supplier.packaging_ref)

                packOb={}

                if(pack.packaging_image != None):

                    packOb["pack_pic"]=getBase64Img(pack.packaging_image)

                    # my_string=my_string.split("'")[1]
                else:
                    packOb["pack_pic"]=''

                packOb["supplier"]=supplier.supplier
                packOb["packaging_ref"]=supplier.packaging_ref
                packOb["packaging_consumption"]=supplier.packaging_consumption
                packOb["packaging_status"]=supplier.packaging_status

                packSuppliers.append(packOb)


def getBrandLogo(file):
    path_prefix=getImagePath()
    fp=path_prefix+str(file)
    try:
        with open(fp, "rb") as img_file:
            my_string=base64.b64encode(img_file.read())
            my_string="data:image/png;base64,"+my_string.decode('utf-8')
    except:
        my_string="data:image/png;base64,"
    return my_string
