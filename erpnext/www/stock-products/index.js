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