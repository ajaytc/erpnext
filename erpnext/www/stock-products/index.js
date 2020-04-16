$(document).ready(function () {
    $('.delete').click((e) => {
        console.log($(e.target).parent().parent())
    })
})


var stock_name =null;
var quantity = $('.selectedproduct:checked').attr('data-qty');

$('#updateStock').on('show.bs.modal', function (event) {
    //var button = $(event.relatedTarget) // Button that triggered the modal
    //var realStock = button.data('watever') // Extract info from data-* attributes
    // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
    // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
    //var stockname = input.data('name')
    stock_name = $('.selectedproduct:checked').attr('data-name')
    quantity = $('.selectedproduct:checked').attr('data-qty')
    var item_name = $('.selectedproduct:checked').attr('data-item')

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
            description : 'Update Stock'
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
                window.location.reload()
            }
        }
    })
    //console.log($('#real-stock').val())
})