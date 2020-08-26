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

    # frappe.get_all('Uniform Order',filters={'brand':brand},)
    # order = frappe.get_doc('Uniform Order', '2d67ae10b1')

    orders = frappe.db.sql("""select uosp.order_no,uosp.quantity,uosp.item_code,uo.customer,uo.point_of_sale,uo.creation from `tabUniform Order` uo inner join `tabUniform order Segment`uos on uos.parent=uo.name inner join `tabUniform Order Segment Products` uosp on uosp.parent=uos.name where uo.brand=%s order by creation desc""", brand)

    # order_no =0
    # quantity=1
    # item_code=2
    # customer=3
    # point_of_sale=4
    # creation=5
    endDates = []
    context.orderSets = {}
    orderN = []

    for order in orders:
        endDateofProduction = calcEndOfProductionDate(order)
        if(endDateofProduction not in endDates):
            orderN = []
            if(order[0] not in orderN):
                endDates.append(endDateofProduction)
                orderN.append(order[0])
                context.orderSets[str(endDateofProduction)] = {}
                context.orderSets[str(endDateofProduction)][str(order[0])] = []

                # context.orderSets[str(endDateofProduction)]=[]
                context.orderSets[str(endDateofProduction)
                                  ][str(order[0])].append(order)
        else:
            if(order[0] not in orderN):
                orderN.append(order[0])
                context.orderSets[str(endDateofProduction)][str(order[0])] = []

                # context.orderSets[str(endDateofProduction)]=[]
                context.orderSets[str(endDateofProduction)
                                  ][str(order[0])].append(order)
            else:
                context.orderSets[str(endDateofProduction)
                                  ][str(order[0])].append(order)

            # context.orderSets[str(endDateofProduction)].append(order)
    # print(context.orderSets)

    # print(orders)
    context=checkMutipleRecs(context)

    return context

def checkMutipleRecs(context):
    context.posNItemDicts={}
    for key,value in context.orderSets.items():
        posNItems={}
        for key2,value2 in context.orderSets[key].items():
            posNItemDict={}
            removeItems=[]
            for order in context.orderSets[key][key2]:
                posNitem=getposNitem(order)
                if(posNitem not in posNItemDict):
                    posNItemDict[str(posNitem)]=order[1]
                else:
                    posNItemDict[str(posNitem)]=int(posNItemDict[str(posNitem)])+int(order[1])
                    # context.orderSets[key][key2].remove(order)
                    removeItems.append(order)
            context.orderSets[key][key2]=removeElements(context.orderSets[key][key2],removeItems)
            posNItems[key2]=posNItemDict
        context.posNItemDicts[key]=posNItems
    return context

def removeElements(orders,removeOrders):
    for removeOrder  in removeOrders:
        orders.remove(removeOrder)
    return orders


def getposNitem(order):
    if(order[4] != None):
        posNitem = order[4]+'-'+order[2]
    else:
        posNitem = order[3]+'-'+order[2]
    return posNitem


def calcEndOfProductionDate(order):
    creationDate = order[5]
    creationDay = creationDate.weekday()

    if(creationDay <= 3):
        dateOfEnd = creationDate + datetime.timedelta(days=(28 - creationDay))
    else:
        dateOfEnd = creationDate + datetime.timedelta(days=(35 - creationDay))

    return dateOfEnd.date()
