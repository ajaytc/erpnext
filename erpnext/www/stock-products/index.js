$(document).ready(function () {
    $('.delete').click((e) => {
        console.log($(e.target).parent().parent())
    })
})


var stock_name = null;
var quantity = $('.selectedproduct:checked').attr('data-qty');
var price = null;

$('#updateStock').on('show.bs.modal', function (event) {

    stock_name = $('.selectedproduct:checked').attr('data-name')
    quantity = $('.selectedproduct:checked').attr('data-qty')
    var item_name = $('.selectedproduct:checked').attr('data-item')
    price = $('.selectedproduct:checked').attr('data-price')

    var modal = $(this)

    modal.find('.modal-title').text('Update Stock of ' + item_name)
    modal.find('.modal-body #in-stock').val(quantity)
    modal.find('.modal-body #real-stock').val(quantity)

})

$('#stockvalidatebutton').click(() => {
    var old_quantity = $('.modal-body #in-stock').val()
    quantity = $('.modal-body #real-stock').val()
    frappe.call({
        method: 'erpnext.modehero.stock.updateStock',
        args: {
            stock_name,
            quantity,
            old_quantity,
            description: 'Update Stock',
            price: price
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
                window.location.reload()
            }
        }
    })

})


var old_stock = $('.selectedproduct:checked').attr('data-qty');

$('#directShip').on('show.bs.modal', function (event) {
    stock_name = $('.selectedproduct:checked').attr('data-name')
    old_stock = $('.selectedproduct:checked').attr('data-qty');
    var item_name = $('.selectedproduct:checked').attr('data-item')
    price = $('.selectedproduct:checked').attr('data-price')

    getSizingDetailsNgeneratetable(stock_name)

    // product = $(e.target).find("option:selected").val()
    // $(e.target).closest('.product-table').attr('id', product)
    // frappe.call({
    //     method: 'erpnext.stock.sizing.getSizes',
    //     args: {
    //         item: product
    //     },
    //     callback: function (r) {
    //         if (!r.exc) {
    //             let table = generateSizingTable(r.message.sizes)
    //             // console.log(table)
    //             $('#sizeTable').html(table)
    //             // $('.qty>td>input').change(priceUpdateCallback)
    //             // getSupplierDetails($('#product').find('option:selected').val())
    //         }
    //     }
    // });

    var modal = $(this)

    modal.find('.modal-title').text('Direct Ship ' + item_name)
})

function getSizingDetailsNgeneratetable(stock) {
    frappe.call({
        method: 'erpnext.stock.sizing.getSizesFromStock',
        args: {
            stock: stock
        },
        callback: function (r) {
            if (!r.exc) {
                let table = generateSizingTable(r.message.sizes)
                // console.log(table)
                if (r.message.sizes.length != 0) {
                    $('#sizeTable').html(table)
                    $('#amountQty').val('')
                    $('#quantitySec').hide()
                } else {
                    $('#sizeTable').html('')
                    $('#quantitySec').show()
                }

                // $('.qty>td>input').change(priceUpdateCallback)
                // getSupplierDetails($('#product').find('option:selected').val())
            }
        }
    });
}

// $('#plNinv').click(function () {


// })

$("#directShip").on("hidden.bs.modal", function () {

    shipOrderName = $('#directShip').attr('data-shiporder')

    if (shipOrderName) {
        frappe.call({
            method: 'erpnext.modehero.shipment_orders.deleteshipment',
            args: {
                shipmentName: shipOrderName
            }, callback: function (r) {
                if (!r.exc) {
                    console.log(r)
                    response_message('','Created Shipment Order Deleted','green')
                    window.location.reload()
                }
            }
        })
    }

});

// $('#directShip').on('show.bs.modal', function (event) {
//     product = $(e.target).find("option:selected").val()
//     $(e.target).closest('.product-table').attr('id', product)
//     frappe.call({
//         method: 'erpnext.stock.sizing.getSizes',
//         args: {
//             item: product
//         },
//         callback: function (r) {
//             if (!r.exc) {
//                 let table = generateSizingTable(r.message.sizes)
//                 // console.log(table)
//                 $(e.target).parent().parent().parent().parent().parent().parent().parent().find('.table-section').html(table)
//                 $('.qty>td>input').change(priceUpdateCallback)
//                 getSupplierDetails($('#product').find('option:selected').val())
//             }
//         }
//     });
// })
function response_message(title, message, color) {
    frappe.msgprint({
        title: __(title),
        indicator: color,
        message: __(message)
    });
}

var needInv=false
$('#plNinv').click(() => {
    needInv=true
    shipOrderName = $('#directShip').attr('data-shiporder')
    if(shipOrderName){
        plNInvGen()
    }else{
        $('#pl-invoice-confirmation').modal('show')
    }
    
})

$('#needShipmentBtn').click(()=>{
    $('#shipment-order-modal').modal('show')
})

$('#noShipmentBtn').click(()=>{
    plNInvGen()
})
function plNInvGen() {
    client = $('#selected-client').val()
    pos = $('#pos-select').val()
    destination = ''

    if (pos) {
        destination = pos
    } else if (client) {
        destination = client
    }

    // console.log(amount)
    console.log(destination)

    
    let qtys = []
    let sizes = []
    let counter = 0

    $('.sizing').map(function () {
        sizes.push($(this).text())
    })
    // regex = /^[0-9]*$/g;
    if($('.sizing').length>0){
        $('.qty>td>input').map(function () {
            if ($(this).val() != "") {
                qty = parseInt($(this).val())
                allnull = false
                qtys.push({
                    size: sizes[counter],
                    quantity: qty
                })
    
    
            }
            counter++
            // qtys.push($(this).val())
        })
    
    
        if (allnull) {
            frappe.throw(frappe._("Please fill quantities"))
        }
    }else{
        amountQty=$('#amountQty').val()
    }
   

    shipOrderName=$('#directShip').attr('data-shiporder')

    frappe.call({
        method: 'erpnext.modehero.stock.directShipfromProductStockNInvoiceGen',
        args: {
            data: {
                stock_name: stock_name,
                qtys: qtys,
                old_stock: old_stock,
                amountQty:amountQty,
                description: destination,
                price: price,
                client: client,
                pos: pos,
                shipOrderName:shipOrderName,

            }

        },
        callback: function (r) {
            if (r.message.status=='ok') {
                console.log(r)
                response_message('Success!!','Invoice and PL Generation Successfull!!','green')
                window.location.reload()
            } else {
                response_message('Invoice Generation Failed!!', r.message.message)
            }
        }
    })
}


$('#shipFromExisting').on('show.bs.modal', function (event) {

    var modal = $(this)

    var client = $('.modal-body #selected-client').val()
    console.log(client)

    $('.selected-client').click(clientUpdateCallback)

    $('.selected-purchase').click(purchaseUpdateCallback)

})

function generateOptions(values) {
    let html = ''
    values.map(v => {
        html += `<option value="${v.name}">${v.name}</option>`
    })
    return html
}

function generateOptions2(values, val_key, txt_key) {
    let html = ''
    html += `<option value="">---:---</option>`
    values.map(v => {
        html += `<option value="${v[val_key]}">${v[txt_key]}</option>`
    })
    return html
}

const clientUpdateCallback = (e) => {
    var client = $(e.target).find("option:selected").val()
    console.log(client)
    frappe.call({
        method: 'erpnext.modehero.stock.get_purchase',
        args: {
            client
        },
        callback: function (r) {
            //console.log(r.message)
            $('#purchase').html(generateOptions(r.message))
        }
    });
}

const purchaseUpdateCallback = (e) => {
    var purchase = $(e.target).find("option:selected").val()
    console.log(purchase)

    frappe.call({
        method: 'erpnext.modehero.stock.get_qps',
        args: {
            purchase
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r.message)
                let table = generateQuantityTables(r.message.quantities)
                console.log(table)
                $('#tables').html(table)
            }
        }
    });
}
var allnull
function generateSizingTable(sizes) {

    let heads = '', inputs = ''

    sizes.map(s => {
        allnull = true
        heads += `<th class="sizing" scope="col">${s}</th>`
        inputs += `<td><input type="text" data-size="${s}" class="form-control sqty"></td>`
    })

    return `
            <table class="table table-bordered" id="product-table">
                <thead>
                    <tr>
                        <th scope="col">{{_("Sizing")}}</th>
                        ${heads}
                    </tr>
                </thead>
                <tbody>
                    <tr class="qty">
                        <th class="qty" scope="row">{{_("Quantity")}}</th>
                        ${inputs}
                    </tr>
                </tbody>
            </table>
    `
}

function generateQuantityTables(quantities) {

    let tables = ''

    for (let i in quantities) {
        let sizes = '', inputs = '', qtys = '', name = ''
        let cal = 0
        quantities[i].map(j => {
            console.log(j)
            cal++
            name = `<th style colspan="${cal}">${j[0]}</th>`
            sizes += `<th scope="col">${j[1]}</th>`
            qtys += `<th scope="col">${j[2]}</th>`
            inputs += `<td><input type="number" class="form-control" value="${j[2]}" min="0" max="${j[2]}"></td>`
        })
        tables += generateTable(sizes, qtys, inputs, name)
    }
    return tables
}

function generateTable(sizes, qtys, inputs, name) {
    return `<table class="table table-bordered">
                <input type="checkbox" class="form-check-input" id="exampleCheck1">
                <tbody>
                    <tr class="name">
                        <th scope="row">{{_("Product Name")}}</th>
                        ${name}
                    </tr>
                    <tr class="sizes">
                        <th scope="row">{{_("Sizes")}}</th>
                        ${sizes}
                    </tr>
                    <tr class="qty">
                        <th scope="row">{{_("Quantity")}}</th>
                        ${qtys}
                    </tr>
                    <tr class="qty-to-ship">
                        <th scope="row">{{_("Quantity to Ship")}}</th>
                        ${inputs}
                    </tr>
                </tbody>
            </table>
    `
}


$('#selected-client').change(function () {
    makePOSList($(this))
    // makePackageList($(this))


})

function makePOSList(el) {
    let client = el.find('option:selected').val()
    frappe.call({
        method: 'erpnext.modehero.uniform.get_pos_of_client',
        args: {
            client
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r.message)
                $('#pos-select').html(generateOptions2(r.message, 'name', 'point_of_sale'))
            }
        }
    })
}