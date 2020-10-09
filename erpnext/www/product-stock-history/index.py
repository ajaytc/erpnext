from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime
from erpnext.modehero.user import haveAccess

no_cache = 1


def get_context(context):
    module = 'stock'
    if(not haveAccess(module)):
        frappe.throw(_("You have not subscribed to this service"),
                     frappe.PermissionError)
    params = frappe.form_dict
    if('stock' in params):
        context.stock = frappe.get_doc('Stock', params.stock)

    context.product = frappe.get_doc("Item", context.stock.product)

    if(context.product.sizing):
        context.sizingSchema = frappe.get_doc(
            'Sizing Scheme', context.product.sizing)

        context.sizingDic=getSizingDic(context)                                 
        context.historyList = frappe.db.sql(
            """select shps.quantity,shps.size,sh.parent,sh.in_out,sh.creation,sh.name,sh.linked_order,sh.order_type from `tabStock History` sh inner join `tabProduct Stock History Per Size` shps on sh.name=shps.parent where sh.parent=%s""", params.stock)

        context.stock=frappe.get_doc('Stock',params.stock)
    # shps.quantity=0
    # shps.size=1
    # sh.parent=2
    # sh.in_out=3
    # sh.creation=4
    # sh.name=5
    # sh.linked_order=6
    #sh.order_type=7


        context.stockHistoryDic= getStockHistoryFormattedDic(context)
      
    else:
        context.stockHistoryDicNOSize = {}
        context.stockHistoryRecsNoSize = frappe.get_list("Stock History", filters={
            'parent': context.stock.name}, fields=["name", "creation", "quantity", "in_out","linked_order","order_type"])

    return context

def getSizingDic(context):
    sizingSchemaDic={}
    sizingSchema=context.sizingSchema

    for sizeOb in sizingSchema.sizing:
        sizingSchemaDic[sizeOb.size]=0
    
    return sizingSchemaDic



def getStockHistoryFormattedDic(context):
    stockHistoryDic = {}

    for rec in context.historyList:
        if(rec[5] not in stockHistoryDic.keys()):
            stockHistoryDic[rec[5]] = {
                'creation':rec[4],
                'in_out':rec[3],
                'order':rec[6],
                'order_type':rec[7]
            }
            sizingDic=getSizingDic(context)
            stockHistoryDic[rec[5]]['sizeNqty']=sizingDic
        
        stockHistoryDic[rec[5]]['sizeNqty'][rec[1]]=rec[0]

    return stockHistoryDic
        
