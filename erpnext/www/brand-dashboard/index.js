
var fabSeen = 0
var trimSeen = 0
var packSeen = 0

$('.selectedShipOrder').change(function () {
    $('#delivered').prop('disabled', false)
})


$('#delivered').click(function () {
    let selectednames = []

    $('input[name="orderCheck"]:checked').each(function () {
        selectednames.push($(this).attr('data-name'))
    });
    console.log(selectednames)

    if (selectednames.length != 0) {
        frappe.call({
            method: 'erpnext.modehero.shipment_orders.deliverOrder',
            args: {
                data: {
                    orders: selectednames
                }
            },
            callback: function (r) {
                if (!r.exc) {
                    console.log(r)
                    location.reload();

                } else {
                    console.log(r)
                }
            }
        })
    } else {
        console.error('Order not selected')

    }


})

$('#fabric_reminder').on('show.bs.modal', function (event) {
    if (fabSeen == 1) {
        $(".fab").hide()
    }
    markSeen('fabric_reminder')
})

$('#pack_reminder').on('show.bs.modal', function (event) {
    if (packSeen == 1) {
        $(".pack").hide()
    }
    markSeen('pack_reminder')
})

$('#trimming_reminder').on('show.bs.modal', function (event) {
    if (trimSeen == 1) {
        $(".trim").hide()
    }
    markSeen('trimming_reminder')
})
$('#fabric_reminder').on('hidden.bs.modal', function (event) {
    fabSeen = 1
    $("#fabCount").html("0")
})

$('#pack_reminder').on('hidden.bs.modal', function (event) {
    packSeen = 1
    $("#packCount").html("0")
})

$('#trimming_reminder').on('hidden.bs.modal', function (event) {
    trimSeen = 1
    $("#trimCount").html("0")
})


function markSeen(item) {
    frappe.call({
        method: 'erpnext.modehero.reminder.markSeen',
        args: {
            data: {
                reminder: item
            }
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)


            } else {
                console.log(r)
            }
        }
    })
}







$('#test').click(function () {

    frappe.call({
        method: 'erpnext.modehero.reminder.order_reminder',
        args: {
            data: {
                orders: "test"
            }
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
                location.reload();

            } else {
                console.log(r)
            }
        }
    })



})