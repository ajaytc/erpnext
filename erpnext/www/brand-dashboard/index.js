
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