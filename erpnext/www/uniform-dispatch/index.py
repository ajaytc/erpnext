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

    orders = frappe.db.sql("""select uos.reciever_name,uosp.order_no,uosp.quantity,uosp.item_code,uo.customer,uo.point_of_sale,uo.creation,uo.name,uosp.size,uosp.recieved,uosp.name,uosp.packing_list,pos.point_of_sale,uosp.invoice from `tabUniform Order` uo inner join `tabUniform order Segment`uos on uos.parent=uo.name inner join `tabUniform Order Segment Products` uosp on uosp.parent=uos.name left join `tabPoint Of Sales` pos on uo.point_of_sale=pos.name where uo.brand=%s order by pos.point_of_sale Asc,customer Asc,reciever_name Asc """, brand)

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
    #uosp.name=10
    # uosp.packing_list=11
    #pos.point_of_sale=12
    # uosp.invoice=13
    
    context.orderSets = {}
    context.posSets={}
    clients=[]
    reciever=[]
    uniformName=[]

    for order in orders:
        client=order[4]
        pos=order[12]
        if(pos!=None and pos!=''):
            primary=pos
        elif (client!=None and client!=''):
            primary=client

        
        context.posSets[primary]={
            'client':client,
            'pos':pos,
            'posName':order[5]
        }
            
        reciever=order[0]
        uniformName=order[7]
        if(primary not in context.orderSets.keys()):
            
            # reciever=[]
            # uniformName=[]
            # clients.append(order[4])
            context.orderSets[primary]={}
            # reciever.append(order[0])
            context.orderSets[primary][reciever]={}
            # uniformName.append(order[7])
            context.orderSets[primary][reciever][uniformName]=[]
            context.orderSets[primary][reciever][uniformName].append(order)
            

        else:
            if(reciever not in context.orderSets[primary].keys()):
                context.orderSets[primary][reciever]={}
                context.orderSets[primary][reciever][uniformName]=[]
                context.orderSets[primary][reciever][uniformName].append(order)
               
            else:
                if(uniformName not in context.orderSets[primary][reciever].keys()):
                    context.orderSets[primary][reciever][uniformName]=[]
                    context.orderSets[primary][reciever][uniformName].append(order)

                else:
                    context.orderSets[primary][reciever][uniformName].append(order)
        
    return context










