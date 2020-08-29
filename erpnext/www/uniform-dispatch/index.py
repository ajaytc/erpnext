from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime


def get_context(context):
    if frappe.session.user == 'Guest':
        frappe.throw(
            _("You need to be logged in to access this page"), frappe.PermissionError)
    roles = frappe.get_roles(frappe.session.user)

    if ("Administrator" not in roles) and ("Brand User" not in roles):
        frappe.throw(_("Not Permitted!"), frappe.PermissionError)

    brand = frappe.get_doc('User', frappe.session.user).brand_name

    orders = frappe.db.sql("""select uos.reciever_name,uosp.order_no,uosp.quantity,uosp.item_code,uo.customer,uo.point_of_sale,uo.creation,uo.name,uosp.size,uosp.recieved from `tabUniform Order` uo inner join `tabUniform order Segment`uos on uos.parent=uo.name inner join `tabUniform Order Segment Products` uosp on uosp.parent=uos.name where uo.brand=%s order by customer Asc,reciever_name Asc """, brand)

    # reciever_name=0
    # order_no =1
    # quantity=2
    # item_code=3
    # customer=4
    # point_of_sale=5
    # creation=6
    # uo.name=7
    #size=8
    #recieved=9
    
    context.orderSets = {}
    clients=[]
    reciever=[]
    uniformName=[]

    for order in orders:
        client=order[4]
        reciever=order[0]
        uniformName=order[7]
        if(client not in context.orderSets.keys()):
            # reciever=[]
            # uniformName=[]
            # clients.append(order[4])
            context.orderSets[client]={}
            # reciever.append(order[0])
            context.orderSets[client][reciever]={}
            # uniformName.append(order[7])
            context.orderSets[client][reciever][uniformName]=[]
            context.orderSets[client][reciever][uniformName].append(order)
        else:
            if(reciever not in context.orderSets[client].keys()):
                context.orderSets[client][reciever]={}
                context.orderSets[client][reciever][uniformName]=[]
                context.orderSets[client][reciever][uniformName].append(order)
            else:
                if(uniformName not in context.orderSets[client][reciever].keys()):
                    context.orderSets[client][reciever][uniformName]=[]
                    context.orderSets[client][reciever][uniformName].append(order)
                else:
                    context.orderSets[client][reciever][uniformName].append(order)
    return context










