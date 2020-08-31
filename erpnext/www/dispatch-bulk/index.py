from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.www.list
import datetime

no_cache = 1


def get_context(context):
    if frappe.session.user == 'Guest':
        frappe.throw(
            _("You need to be logged in to access this page"), frappe.PermissionError)
    roles = frappe.get_roles(frappe.session.user)

    if ("Administrator" not in roles) and ("Brand User" not in roles):
        frappe.throw(_("Not Permitted!"), frappe.PermissionError)

    brand = frappe.get_doc('User', frappe.session.user).brand_name
    orders = frappe.db.sql("""select soi.name,po.name,po.destination_type,soi.item_destination,po.final_destination,po.product_name,po.production_factory,po.carrier,po.tracking_number,po.shipment_date,po.creation,soi.creation,po.internal_ref,soi.parent from `tabProduction Order` po left join `tabSales Order Item`soi on po.name=soi.prod_order_ref where po.brand=%s order by po.creation desc""", brand)
    # 0 = sales_order_item_name
    context.soi_name_index = 0
    # 1 = production_order_name
    # 2 = production_order_destination_type
    # 3 = sales_order_item_destination
    # 4 = production_order_destiantion
    # 5 = product_name
    # 6 = production_factory
    # 7 = carrier_number
    # 8 = tracking_number
    # 9 = shipment_date
    # 10 = po_creation_time
    context.po_creation_time_index = 10
    # 11 = soi_creation_time
    context.soi_creation_time_index = 11
    # 12 = po_internal_ref
    context.if_index = 12
    # 13 = soi_parent_name
    context.soi_parent_index = 13
    # 14 = item_name
    context.item_name_index = 14
    # 15 = item_sizes
    context.sizes_scheme_index = 15
    # 16 = current_stock_sizes_quantities
    context.stock_qty_index = 16
    # 17 = order_size_details
    context.order_qty_index = 17
    # 18 = shipping_history
    context.ship_history_index = 18
    # 19 = POS_or_DESTINY

    orders = list(orders)
    for i in range(len(orders)):
        orders[i] = list(orders[i])
    pos_destination_support_data,item_support_data = collect_item_destination_data(orders)
    orders_with_quantity_data = add_size_quantity_data(orders,item_support_data)
    final_order_list = add_shipment_n_order_number_data(orders_with_quantity_data)
    context.presenting_order_data = modify_order_list(final_order_list,pos_destination_support_data)

    return context

def collect_item_destination_data(orders):
    # if lient order final destination is open to select pos also , then this function should be chnged
    supportive_destination_dic = {"destinations":{},"poss":{}}
    supportive_item_dic = {}
    for order in orders:
        if order[5] not in supportive_item_dic:
            supportive_item_dic[order[5]] = get_item_details(order[5])
        if order[3] in supportive_destination_dic["destinations"] or order[3] in supportive_destination_dic["poss"] or order[4] in supportive_destination_dic["destinations"] or order[4] in supportive_destination_dic["poss"]:
            continue
        if order[2]==None and order[0]!=None and order[3]!=None:
            # this is situation of production order has sales order items by client and destination is a client destination
            destination_data_list = frappe.get_all("Destination",filters={'name':order[3]},fields=['destination_name','client_name'])
            if len(destination_data_list)==0:
                continue
            elif destination_data_list[0].client_name==None:
                continue
            client_data_list = frappe.get_all('Customer',{'name':destination_data_list[0].client_name},['customer_name'])
            if len(client_data_list)==0:
                continue
            supportive_destination_dic["destinations"][order[3]] = {"client_id":destination_data_list[0].client_name,"client_name":client_data_list[0].customer_name}
        elif order[2]==None and order[0]==None:
            continue
        elif int(order[2])==0 and order[0]==None and order[4]!=None:
            # this is situation of bulk order destination is a client destination
            destination_data_list = frappe.get_all("Destination",filters={'name':order[4]},fields=['destination_name','client_name'])
            if len(destination_data_list)==0:
                continue
            elif destination_data_list[0].client_name==None:
                continue
            client_data_list = frappe.get_all('Customer',{'name':destination_data_list[0].client_name},['customer_name'])
            if len(client_data_list)==0:
                continue
            supportive_destination_dic["destinations"][order[4]] = {"client_id":destination_data_list[0].client_name,"client_name":client_data_list[0].customer_name}
        elif int(order[2])==1 and order[0]==None and order[4]!=None:
            # this is situation of bulk order destination is a pos
            pos_data_list = frappe.get_all("Point Of Sale",filters={'name':order[4]},fields=['point_of_sale'])
            if len(pos_data_list)==0:
                continue
            supportive_destination_dic["poss"][order[4]] = {"name":pos_data_list[0].point_of_sale}
    return supportive_destination_dic,supportive_item_dic

def  modify_order_list(orders,support_destination_data):
    result_obj = {}
    for order in orders:
        if order[2]==None and order[0]!=None:
            # this is situation of production order has sales order items by client and destination is a client destination
            client_id = support_destination_data["destinations"][order[3]]["client_id"]
            client_name = support_destination_data["destinations"][order[3]]["client_name"]
            if client_id not in result_obj:
                result_obj[client_id]={"show_name":client_name,"orders":[],"max_col_span":0}
            order.append("destination")
            if len(order[15])>result_obj[client_id]["max_col_span"]: result_obj[client_id]["max_col_span"]=len(order[15])
            result_obj[client_id]["orders"].append(order)
        elif order[2]==None and order[0]==None:
            continue
        elif int(order[2])==0 and order[0]==None:
            # this is situation of bulk order destination is a client destination
            client_id = support_destination_data["destinations"][order[4]]["client_id"]
            client_name = support_destination_data["destinations"][order[4]]["client_name"]
            if client_id not in result_obj:
                result_obj[client_id]={"show_name":client_name,"orders":[],"max_col_span":0}
            order.append("destination")
            if len(order[15])>result_obj[client_id]["max_col_span"]: result_obj[client_id]["max_col_span"]=len(order[15])
            result_obj[client_id]["orders"].append(order)
        elif int(order[2])==1 and order[0]==None:
            # this is situation of bulk order destination is a pos
            if order[4] not in result_obj:
                result_obj[order[4]]={"show_name":support_destination_data["poss"][order[4]]["name"],"orders":[],"max_col_span":0}
            order.append("pos")
            if len(order[15])>result_obj[client_id]["max_col_span"]: result_obj[client_id]["max_col_span"]=len(order[15])
            result_obj[order[4]]["orders"].append(order)
    return result_obj

def add_size_quantity_data(orders,item_support):
    for i in range(len(orders)):
        orders[i].append(item_support[orders[i][5]]["item_name"])
        orders[i].append(item_support[orders[i][5]]["sizes"])
        orders[i].append(item_support[orders[i][5]]["current_stock_sizes_quantities"])
        try:
            if orders[i][0]!=None:
                orders[i].append(frappe.get_all('Quantity Per Size',{'order_id':orders[i][0]},['size','quantity']))
            elif orders[i][1]!=None:
                orders[i].append(frappe.get_all('Production Quantity Per Size',{'parent':orders[i][1]},['size','quantity']))
        except Exception:
            orders[i].append(None)
    return orders

def add_shipment_n_order_number_data(orders):
    for i in range(len(orders)):
        ship_order_docs = []
        ship_list = frappe.get_all('Shipment Order',{'internal_ref_prod_order':orders[i][12]},['name'])

        for ship_order in ship_list:
            ship_doc = frappe.get_doc("Shipment Order",ship_order.name)
            temp_list = []
            for qps in ship_doc.shipment_quantity_per_size:
                temp_list.append({"size":qps.size,"quantity":qps.quantity})
            ship_order_docs.append({"date":ship_doc.creation,"quantity_per_size":temp_list})

        orders[i].append(ship_order_docs)
    return orders

def get_item_details(item):
    if item==None:
        return None
    resul_obj = {}
    try:
        item_doc = frappe.get_doc("Item",item)
        resul_obj["item_name"] = item_doc.item_name 
        if item_doc.sizing==None:
            resul_obj["sizes"] = None
        else:
            resul_obj["sizes"] = frappe.get_all('Sizing', filters={'parent': item_doc.sizing}, fields=['size'],order_by='idx')
        c = frappe.get_doc("Stock",frappe.get_all("Stock",filters={"parent":item})[0].name).product_stock_per_size
        sqlist = []
        for sq in c:
            sqlist.append({"size":sq.size,"quantity":sq.quantity})
        resul_obj["current_stock_sizes_quantities"] = sqlist
    except Exception:
        resul_obj["sizes"] = None
        resul_obj["item_name"] = None
        resul_obj["current_stock_sizes_quantities"] = None
    return resul_obj
                





