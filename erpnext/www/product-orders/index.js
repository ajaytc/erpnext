
$('#validate').click(function () {
    let orders = {}

    $('.order-select:checked').map(function () {
        let orderId = $(this).attr('data-order')
        let table = $(`#${orderId}`)
        let order = {}
        table.find('.modified-qty').map(function () {
            if ($(this).val() != '') {
                order[$(this).attr('data-size')] = $(this).val()
            }
        })
        if (Object.keys(order).length > 0) {
            orders[orderId] = order
        }
    })
    console.log(orders)
    frappe.call({
        method: 'erpnext.modehero.sales_order.validate_multiple_orders',
        args: {
            orders
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r.message)
                window.location.reload()
            }
        }
    });
})