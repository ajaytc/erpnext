$(document).ready(function () {
    $('.delete').click((e) => {
        console.log($(e.target).parent().parent())
    })
})

var stock_name =null;
var price = null;
var in_stock = null;
var fabric_name = null;
var old_stock =null

$('#updateStock').on('show.bs.modal', function (event) {

    stock_name = $('.selectedfabric:checked').attr('data-name')
    in_stock = $('.selectedfabric:checked').attr('data-stock')
    old_stock = $('.selectedfabric:checked').attr('data-stock')
    fabric_name = $('.selectedfabric:checked').attr('data-item')
    unit_price = $('.selectedfabric:checked').attr('data-price')

    var modal = $(this)

    modal.find('.modal-title').text('Update Stock of ' + fabric_name)
    modal.find('.modal-body #in-stock').val(old_stock)
    modal.find('.modal-body #real-stock').val(in_stock)

})

$('#validatebutton').click(() => {
    in_stock = $('.modal-body #real-stock').val()

    console.log("Old Stock:"+old_stock)
    console.log("New Stock:"+in_stock)

    frappe.call({
        method: 'erpnext.modehero.stock.updateStock',
        args: {
            stock_name,
            quantity : in_stock,
            old_quantity : old_stock,
            description : 'Update Stock',
            price : unit_price
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
                window.location.reload()
            }
        }
    })

})

$('#directShip').on('show.bs.modal', function (event) {
    stock_name = $('.selectedfabric:checked').attr('data-name')
    in_stock = $('.selectedfabric:checked').attr('data-stock')
    old_stock = $('.selectedfabric:checked').attr('data-stock')
    fabric_name = $('.selectedfabric:checked').attr('data-item')
    unit_price = $('.selectedfabric:checked').attr('data-price')

    var modal = $(this)

    modal.find('.modal-title').text('Direct Ship ' + fabric_name)
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
            price : unit_price
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
                window.location.reload()
            }
        }
    })
    console.log(amount+ " of "+ fabric_name+ " shipped to " + destination)
})

$('#shipFromExisting').on('show.bs.modal', function (event) {

    var modal = $(this)

    var vendor = $('.modal-body #selected-vendor').val()
    console.log(vendor)

    $('.selected-vendor').click(vendorUpdateCallback)

    //$('.selected-purchase').click(purchaseUpdateCallback)
    
})

function generateOptions(values) {
    let html = ''
    values.map(v => {
        html += `<option value="${v.name}">${v.name}</option>`
    })
    return html
}

const vendorUpdateCallback = (e) => {
    var vendor = $(e.target).find("option:selected").val()
    console.log(vendor)
    frappe.call({
        method: 'erpnext.modehero.stock.get_fabric_orders',
        args: {
            vendor
        },
        callback: function (r) {
            //console.log(r.message)
            $('#orders').html(generateOptions(r.message))
        }
    });
}