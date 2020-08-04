from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime
import base64
import os
from frappe.utils.pdf import getBase64Img

no_cache = 1
path_prefix = "/home/dhananjana/python_project/modehero/sites/modehero.com/public"


def get_context(context):
    fabSuppliers = []
    trimSuppliers = []
    packSuppliers = []
    params = frappe.form_dict
    if('order' in params):
        context.order = frappe.get_doc('Production Order', params.order)

    

    user = frappe.get_doc('User', frappe.session.user)

    context.product = frappe.get_doc('Item', context.order.product_name)

    getSuppliers(context.order, fabSuppliers,
                 trimSuppliers, packSuppliers)
    brand_name = frappe.get_doc('User', frappe.session.user).brand_name

    brand = frappe.get_all("User", filters={"type": "brand", "brand_name": brand_name}, fields=[
        "user_image", "address1", "name"])

    context.brand_logo = getBrandLogo(brand[0].user_image)
    context.address=brand[0].address1


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

    # context.parents = [
    #     {"name": frappe._("Home"), "route": "/"}
    # ]

    return context


def getSuppliers(order, fabSuppliers, trimSuppliers, packSuppliers):

    suppliers = order.suppliers

    for supplier in suppliers:
        if(supplier.supplier_group == 'Fabric'):
            if(supplier.fabric_ref != ''):

                fabric = frappe.get_doc("Fabric", supplier.fabric_ref)

                fabSupplierOb = {}
                if(fabric.fabric_image != None):
                    fp = path_prefix+str(fabric.fabric_image)
                    with open(fp, "rb") as img_file:
                        my_string = base64.b64encode(img_file.read())
                        my_string = my_string.decode('utf-8')
                        fabSupplierOb["fabric_pic"] = getBase64Img(fabric.fabric_image)

                        # my_string=my_string.split("'")[1]
                else:
                    fabSupplierOb["fabric_pic"] = ''

                fabSupplierOb["supplier"] = supplier.supplier
                fabSupplierOb["fabric_ref"] = supplier.fabric_ref
                fabSupplierOb["fabric_consumption"] = supplier.fabric_consumption
                fabSupplierOb["fabric_status"] = supplier.fabric_status

                fabSupplierOb["color"] = fabric.color
                fabSupplierOb["width"] = fabric.width
                fabSupplierOb["fabric_way"] = fabric.fabric_way
                fabSuppliers.append(fabSupplierOb)
        elif (supplier.supplier_group == 'Trimming'):
            if(supplier.trimming_ref != ''):
                trim = frappe.get_doc("Trimming Item", supplier.trimming_ref)

                trimOb = {}
                if(trim.trimming_image != None):
                    fp = path_prefix+str(trim.trimming_image)
                    with open(fp, "rb") as img_file:
                        my_string = base64.b64encode(img_file.read())
                        my_string = my_string.decode('utf-8')
                        trimOb["trim_pic"] = "data:image/png;base64,"+my_string

                        # my_string=my_string.split("'")[1]
                else:
                    trimOb["trim_pic"] = ''

                trimOb["supplier"] = supplier.supplier
                trimOb["trimming_ref"] = supplier.trimming_ref
                trimOb["trimming_consumption"] = supplier.trimming_consumption
                trimOb["trimming_status"] = supplier.trimming_status

                trimOb["color"] = trim.color
                trimOb["size"] = trim.trimming_size

                trimSuppliers.append(trimOb)
        elif (supplier.supplier_group == 'Packaging'):
            if(supplier.packaging_ref != ''):
                pack = frappe.get_doc("Packaging Item", supplier.packaging_ref)

                packOb = {}

                if(pack.packaging_image != None):
                    fp = path_prefix+str(pack.packaging_image)
                    with open(fp, "rb") as img_file:
                        my_string = base64.b64encode(img_file.read())
                        my_string = my_string.decode('utf-8')
                        packOb["pack_pic"] = "data:image/png;base64,"+my_string

                        # my_string=my_string.split("'")[1]
                else:
                    packOb["pack_pic"] = ''

                packOb["supplier"] = supplier.supplier
                packOb["packaging_ref"] = supplier.packaging_ref
                packOb["packaging_consumption"] = supplier.packaging_consumption
                packOb["packaging_status"] = supplier.packaging_status

                packSuppliers.append(packOb)


def getBrandLogo(file):
    fp = path_prefix+str(file)
    with open(fp, "rb") as img_file:
        my_string = base64.b64encode(img_file.read())
        my_string = "data:image/png;base64,"+my_string.decode('utf-8')
    
    return my_string
