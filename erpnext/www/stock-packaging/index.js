$(document).ready(function () {
    $('.delete').click((e) => {
        console.log($(e.target).parent().parent())
    })
})


var stock_name =null;
var price = null;
var in_stock = null;
var packaging_name = null;
var old_stock =null

$('#updateStock').on('show.bs.modal', function (event) {

    stock_name = $('.selectedpackaging:checked').attr('data-name')
    in_stock = $('.selectedpackaging:checked').attr('data-stock')
    old_stock = $('.selectedpackaging:checked').attr('data-stock')
    packaging_name = $('.selectedpackaging:checked').attr('data-item')
    unit_price = $('.selectedpackaging:checked').attr('data-price')

    var modal = $(this)

    modal.find('.modal-title').text('Update Stock of ' + packaging_name)
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
    stock_name = $('.selectedpackaging:checked').attr('data-name')
    in_stock = $('.selectedpackaging:checked').attr('data-stock')
    old_stock = $('.selectedpackaging:checked').attr('data-stock')
    packaging_name = $('.selectedpackaging:checked').attr('data-item')
    unit_price = $('.selectedpackaging:checked').attr('data-price')

    var modal = $(this)

    modal.find('.modal-title').text('Direct Ship ' + packaging_name)
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
            price : unit_price,
            order_type:'directship-packaging'
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