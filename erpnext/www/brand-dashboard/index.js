
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

$('.list-group-item.form-modal').click(function(){
    group = $(this).data('group')
    $('#form_modal').attr('data-group',group.charAt(0).toUpperCase() + group.substring(1))
    $('#form_group_name').text(group) 
})

$('#create_vendor').submit(function() {
    var $inputs = $('#create_vendor :input');
    var values = {};
    $inputs.each(function() {
        values[this.name] = $(this).val();
    }); 

    validation_report = validate_supply_form(values)
    if (validation_report.status!="ok"){
        frappe.msgprint({
            title: __('Error'),
            indicator: 'red',
            message: __(validation_report.message)
        });
        return null
    }
    values["supply_group"] = $('#form_modal').data('group')
    // Here supply group is taken from the data-group attribute given from the button of the sidebar
    create_supplier(values)
});

function create_supplier(data){
    frappe.call({
        method: 'erpnext.modehero.supplier.create_supplier',
        args: {
            data: {
                email : data.supply_email,
                supplier_group : data.supply_group,
                address1 : data.supply_ad1,
                address2 : data.supply_ad2,
                contact : data.supply_contact,
                phone_number : data.supply_phone,
                city : data.supply_city,
                zip_code : data.supply_zip,
                supplier_name : data.supply_name
            }
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
                let supplier = r.message.supplier
                if (supplier && supplier.name) {
                    frappe.msgprint({
                        title: __('Notification'),
                        indicator: 'green',
                        message: __('Supplier' + supplier.name + ' created successfully')
                    });
                }
            }
        }
    })
}

function validate_supply_form(input){
    for (var key of Object.keys(input)) {   
        if (key!="" && key!="supply_ad1" && key!="supply_ad2" && String(input[key]).trim()==""){
            return {status:"not" , message:"Please fill all required fields!"}
        }
    }
    if (!validate_phone(input['supply_phone'])){
        return {status:"not" , message:"Please enter correct inputs!"}
    }
    if (!validate_email(input['supply_email'])){
        return {status:"not" , message:"Please enter correct inputs!"}
    }
    if (!validate_zipcode(input['supply_zip'])){
        return {status:"not" , message:"Please enter correct inputs!"}
    }
    return {status:"ok" , message:"Succesfull!"}
}   

function validate_email(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

function validate_phone(inputtxt) {
    var phoneno = /^\+?([0-9]{2})\)?[-. ]?([0-9]{4})[-. ]?([0-9]{4})$/;
    if(String(inputtxt).match(phoneno)) {
      return true;
    }  
    else {  
      return false;
    }
}

function validate_zipcode(elementValue){
    var zipCodePattern = /^\d{5}$|^\d{5}-\d{4}$/;
     return zipCodePattern.test(elementValue);
}

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