$('#validatebtn').click(function () {
    validate(true)
})

$('#not-validate').click(function () {
    validate(false)
})

function validate(isvalidate) {
    let lastorder = ''
    $('.selected').map(function () {
        if ($(this).prop('checked')) {
            console.log($(this))
            if (lastorder !== $(this).attr('data-order')) {
                console.log(lastorder)
                lastorder = $(this).attr('data-order')
                frappe.call({
                    method: 'erpnext.modehero.prototype.validate',
                    args: {
                        order: lastorder,
                        isvalidate
                    },
                    callback: function (r) {
                        if (!r.exc) {
                            console.log(r)
                            let order = r.message.order
                            if (order && order.name) {
                                $('#order-no').html(order.name)
                                frappe.msgprint({
                                    title: __('Notification'),
                                    indicator: 'green',
                                    message: __('Sales order ' + order.name + ' created successfully')
                                });
                                window.location.reload()
                            }
                        }
                    }
                })
            }
        }
    })
}