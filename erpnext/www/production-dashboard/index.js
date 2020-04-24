$('#validatebtn').click(function () {
    validate(true)
})

$('#not-validate').click(function () {
    validate(false)
})

$('#finished').click(function () {
    if ($(this).attr('data-btntype') == "pro-finish") {
        set_finish("production")
    }
    else if ($(this).attr('data-btntype') == "pre-finish") {
        set_finish("prototype")
    }
})

$('.nav-link').click(function () {
    if (($(this).attr('id') == "pre-pro-fin") || ($(this).attr('id') == "pro-fin")) {
        $('#finished').hide()
    }
    else if ($(this).attr('id') == "pre-pro-on-pro") {
        $('#finished').show()
        $('#finished').attr('data-btntype', "pre-finish")
    }
    else if ($(this).attr('id') == "pro-on-pro") {
        $('#finished').show()
        $('#finished').attr('data-btntype', "pro-finish")
    }
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
                            }
                        }
                    }
                })
            }
        }
    })
}

function set_finish(order_type) {
    let temp_order_list = []
    $('.selected').map(function () {
        if ($(this).prop('checked')) {
            temp_order_list.push($(this).attr('data-order'));
        }
    })
    if (temp_order_list.length > 0) {
        frappe.call({
            method: 'erpnext.modehero.' + order_type + '.set_finish',
            args: {
                orderslist: temp_order_list,
            },
            callback: function (r) {
                if (r) {
                    if (r.message['status'] == "ok") {
                        response_message('Successfull', 'Orders finished successfully', 'green')
                        window.location.reload()
                        return null;
                    }
                    response_message('Unsuccessfull', 'Orders finished unsuccessfully', 'red')
                    window.location.reload()
                    return null
                }
                response_message('Unsuccessfull', 'Orders finished unsuccessfully', 'red')
            }
        })
    }
}

function response_message(title, message, color) {
    frappe.msgprint({
        title: __(title),
        indicator: color,
        message: __(message)
    });
}