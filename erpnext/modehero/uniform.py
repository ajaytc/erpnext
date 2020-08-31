import frappe
import json
import ast
import datetime
from frappe.utils.pdf import getBase64Img, getImagePath
from frappe.utils.print_format import report_to_pdf


@frappe.whitelist()
def get_pos_of_client(client):
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    pos_list = frappe.get_all("Point Of Sales", filters={
                              'parent_company': client, 'brand': brand}, fields=['point_of_sale', 'name'])
    return pos_list


@frappe.whitelist()
def get_packages_of_client(client):
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    package_list = frappe.get_all("Package", filters={
                                  'client': client, 'brand': brand}, fields=['package_name', 'name'])
    return package_list


@frappe.whitelist()
def get_products_of_package(packageName):
    package = frappe.get_doc("Package", packageName)
    productQtys = package.package_quantity
    productDetails = []

    for product in productQtys:
        productName = product.item_code
        productOb = frappe.get_doc('Item', productName)
        prod = {
            'item_name': productOb.item_name,
            'qty': product.quantity,
            'item_code': productOb.name
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
    segments = []
    for segment in data['segments']:
        recieverName = segment['name']
        productDetails = []

        for productDetail in segment['segmentProducts']:
            product = {}
            product['item_code'] = productDetail['item_code']
            product['order_no'] = productDetail['orderNum']
            product['quantity'] = productDetail['qty']
            product['size'] = productDetail['size']
            product['comment'] = productDetail['comment']

            productDetails.append(product)

        segment = {}
        segment['reciever_name'] = recieverName
        segment['segment_products'] = productDetails

        segments.append(segment)

    order = frappe.get_doc({
        'doctype': 'Uniform Order',
        'brand': brand,
        'customer': data['client'],
        'point_of_sale': data['pos'],
        'package': data['package'],
        'order_segments': segments
    })

    order.insert()
    frappe.db.commit()
    updateSegmentProductDetails(data, order)

    return order


def updateSegmentProductDetails(data, order):

    # frappe.get_all('Uniform order Segment',filters={'parent':order.name},fields=['name','reciever_name'])
    segments = order.order_segments

    for segment in segments:
        for product in segment.segment_products:
            product.parent = segment.name
            product.insert(ignore_permissions=True)

    frappe.db.commit()


@frappe.whitelist()
def getSizesDetails(data):
    data = json.loads(data)
    user = frappe.get_doc('User', frappe.session.user)
    brand = user.brand_name
    order_no = data['order_no']
    item_code = data['item_name']

    sizeDetails = frappe.db.sql("""select uosp.order_no,uosp.quantity,uosp.item_code,uo.customer,uos.reciever_name,uosp.size,uo.creation,uosp.name from `tabUniform Order` uo inner join `tabUniform order Segment`uos on uos.parent=uo.name inner join `tabUniform Order Segment Products` uosp on uosp.parent=uos.name where uo.brand=%s and uosp.order_no=%s and uosp.item_code=%s order by creation desc""", (brand, order_no, item_code))

    # order_no=0
    # qty=1
    # item_code=2
    # customer=3
    # reciever_name=4
    # size=5
    # creation=6
    # uosp.name=7

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


@frappe.whitelist()
def recieveOrderPieces(data):
    data = json.loads(data)
    orderPieces = data['pieces']

    for pieceName in orderPieces:
        piece = frappe.get_doc('Uniform Order Segment Products', pieceName)
        piece.recieved = 1

        piece.save(ignore_permissions=True)

    frappe.db.commit()

    return {'status': 'ok'}


@frappe.whitelist()
def generatePl(data):
    data = json.loads(data)
    client = frappe.get_doc('Customer', data['client'])
    
    clientAddress = getClientAddress(client)
    # destinationAddress=getDestinationAddress(data['pos'])
    packProductDetails = data['packProductDetails']

    brand_name = frappe.get_doc('User', frappe.session.user).brand_name
    brand = frappe.get_all("User", filters={"type": "brand", "brand_name": brand_name}, fields=[
        "user_image", "address1", "name"])
    # brand = user.brand_name

    templateDetails = {}

    if(brand[0].user_image != None and brand[0].user_image != ''):
        brand_logo = getBase64Img(brand[0].user_image)
        # templateDetails['brand_logo'] = brand_logo

    templateDetails['address'] = brand[0].address1
    templateDetails['creation'] = datetime.datetime.now()
    templateDetails['client_name'] = client.name
    templateDetails['client_address'] = clientAddress
    templateDetails['destination'] = 'Destination Address'
    templateDetails['packProductDetails'] = packProductDetails
    temp = frappe.get_all("Pdf Document", filters={"type": "Packing List"}, fields=[
        "content", "type", "name"])

    generatedPl = frappe.render_template(temp[0]['content'], templateDetails)
    packingList = storePL(generatedPl, brand_name)
    recordOnPieces(packingList, packProductDetails)

    return {'status': 'ok'}


def recordOnPieces(packingList, packProductDetails):
    for pack, packValue in packProductDetails.items():
        for piece in packProductDetails[pack]:
            pieceOb = frappe.get_doc(
                'Uniform Order Segment Products', piece['name'])
            pieceOb.packing_list = packingList.name
            pieceOb.save(ignore_permissions=True)


def storePL(pl, brand_name):
    packingList = frappe.get_doc({
            'doctype': 'Packing List',
            'content': pl,
            'brand': brand_name
        })
    packingList.insert()
    frappe.db.commit()

    return packingList


@frappe.whitelist()
def displayPLDoc(data):
    data = json.loads(data)
    packingListName = data['packlist_name']

    packingList = frappe.get_doc('Packing List', packingListName)

    brand = frappe.get_all("User", filters={"type": "brand", "brand_name": packingList.brand}, fields=[
        "user_image", "address1", "name"])

    if(brand[0].user_image != None and brand[0].user_image != ''):
            brand_logo = getBase64Img(brand[0].user_image)
    else:
        brand_logo=''
    
    plDetails={}
    plDetails['content']=packingList.content
    plDetails['brand_logo']=brand_logo

    return plDetails





    


def getClientAddress(client):
    clientAddress=''
    if(client.address_line_1!=None):
        clientAddress=clientAddress+client.address_line_1
    if(client.address_line_2!=None):
        clientAddress=clientAddress+client.address_line_2
    
    return clientAddress
        
def getDestinationAddress(pos):
    destinationAddress=''
    pos = frappe.get_doc('Point Of Sales',pos)
    

def getBrandLogo(file):
    path_prefix=getImagePath()
    fp = path_prefix+str(file)
    try:
        with open(fp, "rb") as img_file:
            my_string = base64.b64encode(img_file.read())
            my_string = "data:image/png;base64,"+my_string.decode('utf-8')
    except(e):
        print(e)
        my_string = "data:image/png;base64,"
    return my_string


