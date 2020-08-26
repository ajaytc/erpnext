import frappe
import json
import ast
import datetime

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
            'item_name':productOb.item_name,
            'qty':product.quantity,
            'item_code':productOb.name
        };
        productDetails.append(prod)


    return productDetails

@frappe.whitelist()
def createUniformOrder(data):
    print('dddddd')
    data = json.loads(data)
    # uniOrder=frappe.get_doc('Uniform Order','43aeef2abf')

    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    # orderSegment=frappe.get_doc({
    #     'doctype':'Uniform order Segment',
    #     'reciever_name':data['']

    # })
    segments=[]
    for segment in data['segments']:
        recieverName=segment['name']
        productDetails=[]

        for productDetail in segment['segmentProducts']:
            product={}
            product['item_code']=productDetail['item_code']
            product['order_no']=productDetail['orderNum']
            product['quantity']=productDetail['qty']
            product['size']=productDetail['size']
            product['comment']=productDetail['comment']

            productDetails.append(product)
        

        segment={}
        segment['reciever_name']=recieverName
        segment['segment_products']=productDetails

        
        segments.append(segment)


    order=frappe.get_doc({
        'doctype':'Uniform Order',
        'brand': brand,
        'customer':data['client'],
        'point_of_safe':data['pos'],
        'package':data['package'],
        'order_segments':segments
    })

    order.insert()
    frappe.db.commit()
    updateSegmentProductDetails(data,order)

    return order

def updateSegmentProductDetails(data,order):

    # frappe.get_all('Uniform order Segment',filters={'parent':order.name},fields=['name','reciever_name'])
    segments=order.order_segments

    for segment in segments:
        for product in segment.segment_products:
            product.parent=segment.name
            product.insert(ignore_permissions=True)
        
    frappe.db.commit()

@frappe.whitelist()
def getSizesDetails(data):
    data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    order_no=data['order_no']
    item_code=data['item_name']

    sizeDetails=frappe.db.sql("""select uosp.order_no,uosp.quantity,uosp.item_code,uo.customer,uos.reciever_name,uosp.size,uo.creation from `tabUniform Order` uo inner join `tabUniform order Segment`uos on uos.parent=uo.name inner join `tabUniform Order Segment Products` uosp on uosp.parent=uos.name where uo.brand=%s and uosp.order_no=%s and uosp.item_code=%s order by creation desc""",(brand,order_no,item_code))
    
    # order_no=0
    # qty=1
    # item_code=2
    # customer=3
    # reciever_name=4
    # size=5
    # creation=6

    return sizeDetails



def calcEndOfProductionDate(order):
    creationDate = order[5]
    creationDay = creationDate.weekday()

    if(creationDay <= 3):
        dateOfEnd = creationDate + datetime.timedelta(days=(28 - creationDay))
    else:
        dateOfEnd = creationDate + datetime.timedelta(days=(35 - creationDay))

    return dateOfEnd.date()
    # for segmentIdx in range(0,len(data['segments'])) :
        
    #     recieverName=segment['name']
        # productDetails=[]

        # for productDetail in segment['segmentProducts']:
        #     product={}
        #     product['item_code']=productDetail['item_code']
        #     product['order_no']=productDetail['orderNum']
        #     product['quantity']=productDetail['qty']
        #     product['size']=productDetail['size']

        #     productDetails.append(product)
        

        # segment={}
        # segment['reciever_name']=recieverName
        # segment['segment_products']=productDetails

    # order = frappe.get_doc({
    #     'doctype': 'Fabric Order',
    #     'brand': brand,
    #     'fabric_vendor': data['fabric_vendor'],
    #     'internal_ref': data['internal_ref'],
    #     'fabric_ref': data['fabric_ref'],
    #     'product_name': data['item_code'],



