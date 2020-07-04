
var fabSeen = 0
var trimSeen = 0
var packSeen = 0

var checked;

$('.selectedShipOrder').change(function () {
    // $('#delivered').prop('disabled', false)
    checked=$('.selectedShipOrder').is(':checked'); 
    if(checked){
        $('#delivered').prop('disabled', false)
    }else{
        $('#delivered').prop('disabled', true)
    }
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

$('.delete_reminder').click(function () {
    if ($(this).attr('data-remtype') == "fabric") {
        delete_reminder("fabric")
    }
    else if ($(this).attr('data-remtype') == "trimming") {
        delete_reminder("trimming")
    }
    else if ($(this).attr('data-remtype') == "packaging") {
        delete_reminder("packaging")
    }
})

function delete_reminder(type){
    let temp_reminder_list = []
    let check_box_class = "reminder_selected_" + type
    $("."+check_box_class).map(function () {
        if ($(this).prop('checked')) {
            temp_reminder_list.push($(this).attr('data-reminder'));
        }
    })
    if (temp_reminder_list.length > 0) {
        frappe.call({
            method: 'erpnext.modehero.reminder.deleteReminder',
            args: {
                reminderslist: temp_reminder_list,
            },
            callback: function (r) {
                if (r) {
                    if (r.message['status'] == "ok") {
                        response_message('Successfull', 'Reminders deleted successfully', 'green')
                        window.location.reload()
                        return null;
                    }
                    response_message('Unsuccessfull', 'Reminders deleted unsuccessfully', 'red')
                    window.location.reload()
                    return null
                }
                response_message('Unsuccessfull', 'Reminders deleted unsuccessfully', 'red')
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