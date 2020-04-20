$(document).ready(function () {
    $('.delete').click((e) => {
        console.log($(e.target).parent().parent())
    })
})


var stock_name =null;
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

$('#validatebutton').click(() => {
    var old_quantity = $('.modal-body #in-stock').val()
    quantity = $('.modal-body #real-stock').val()
    frappe.call({
        method: 'erpnext.modehero.stock.updateStock',
        args: {
            stock_name,
            quantity,
            old_quantity,
            description : 'Update Stock',
            price : price
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

    var modal = $(this)

    modal.find('.modal-title').text('Direct Ship ' + item_name)
})

$('#shipbutton').click(() => {
    var amount = $('.modal-body #quantity').val()
    var destination = $('.modal-body #destination').val()
    
    console.log(amount)
    console.log(destination)

    frappe.call({
        method: 'erpnext.modehero.stock.directShip',
        args: {
            stock_name,
            amount,
            old_stock,
            description : destination,
            price : price
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
                window.location.reload()
            }
        }
    })
})


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

function generateQuantityTables(quantities) {

    let tables = ''

    for (let i in quantities) {
        let sizes = '', inputs = '',qtys ='',name = ''
        let cal =0
        quantities[i].map(j => {
            console.log(j)
            cal++
            name = `<th style colspan="${cal}">${j[0]}</th>`
            sizes += `<th scope="col">${j[1]}</th>`
            qtys += `<th scope="col">${j[2]}</th>`
            inputs += `<td><input type="number" class="form-control" value="${j[2]}" min="0" max="${j[2]}"></td>`
        })
        tables += generateTable(sizes, qtys,  inputs, name)
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
