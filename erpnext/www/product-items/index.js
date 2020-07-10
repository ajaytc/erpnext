$(".grid-add-row").click(function () {

    var markup = "<tr><td><input type='checkbox' class='checkRec'></td><td><input type='text' class='input-with-feedback form-control bold in  put-sm' placeholder='From'></td><td><input type='text' class='input-with-feedback form-control bold in  put-sm' placeholder='To'></td><td><input type='text' class='input-with-feedback form-control bold in  put-sm' placeholder='Price'></td></tr>";
    $("table tbody").append(markup);
});

// Find and remove selected table rows
$(".grid-remove-rows").click(function () {
    $("table tbody").find('input[class="checkRec"]').each(function () {
        if ($(this).is(":checked")) {
            $(this).parents("tr").remove();
        }
    });
});

// $('.check').change(function () {
//     if (this.checked) {
//         $('#del_row').css("display","block")
//     }else{
//         $('#del_row').css("display","none")
//     }
// });

var checked;

$("table tbody").find('input[class="checkRec"]').change(function () {
    console.log("ddddddddd")
    // $('#delivered').prop('disabled', false)
    checked = $('.checkRec').is(':checked');
    if (checked) {
        $('#del_row').css("display", "block")
    } else {
        $('#del_row').css("display", "none")
    }
})


$('.fab_sup').click(function () {
    var el = $(this)
    frappe.call({
        method: 'erpnext.modehero.fabric.get_fabric',
        args: {
            vendor: $(this).val()
        },
        callback: function (r) {
            // console.log($(this).closest('.row'))
            el.closest('.row').find('#fab_ref_list option').remove();
            // $('#fab_ref_list option').remove()
            $.each(r.message, function (key, value) {

                el.closest('.row').find('#fab_ref_list').append((`<option value="${value.fabric_ref}"> 
                                       ${value.name} 
                                  </option>`));
            });

        }
    })
})


$('.trim_sup').click(function () {
    var el = $(this)
    frappe.call({
        method: 'erpnext.modehero.trimming.get_item',
        args: {
            vendor: $(this).val()
        },
        callback: function (r) {
            console.log(r)
            el.closest('.row').find('#trim_ref_list option').remove();
            // $('#trim_ref_list option').remove()
            $.each(r.message, function (key, value) {

                el.closest('.row').find('#trim_ref_list').append((`<option value="${value.internel_ref}"> 
                                       ${value.name} 
                                  </option>`));
            });

        }
    })
})

$('.pack_sup').click(function () {
    var el = $(this)
    frappe.call({
        method: 'erpnext.modehero.package.get_item',
        args: {
            vendor: $(this).val()
        },
        callback: function (r) {
            console.log(r)
            el.closest('.row').find('#pack_ref_list option').remove();
            // $('#pack_ref_list option').remove()
            $.each(r.message, function (key, value) {

                el.closest('.row').find('#pack_ref_list').append((`<option value="${value.internel_ref}"> 
                                       ${value.name} 
                                  </option>`));
            });

        }
    })
})

// $(".grid-add-row").click(function () {

//     var markup = "<tr><td><input type='checkbox' class='checkRec'></td><td><input type='text' class='input-with-feedback form-control bold in  put-sm' placeholder='From'></td><td><input type='text' class='input-with-feedback form-control bold in  put-sm' placeholder='To'></td><td><input type='text' class='input-with-feedback form-control bold in  put-sm' placeholder='Price'></td></tr>";
//     $("table tbody").append(markup);
// });

var fabRowCount = 1;
var trimRowCount = 1;
var packRowCount = 1;


$('#addFab').click(function () {
    if (fabRowCount < trimRowCount || fabRowCount < packRowCount) {
        $('.fab').first().clone(true).appendTo($(".service").last())
    } else {
        if (fabRowCount % 2 == 0) {
            var serviceRow = "<div style='background-color: #dddddd;' class='row service'></div>"
        } else {
            var serviceRow = "<div class='row service'></div>"
        }

        $(".card-body").append(serviceRow)
        $('.fab').first().clone(true).appendTo($(".service").last())
    }

    fabRowCount = fabRowCount + 1


})

$('#addTrim').click(function () {
    if (trimRowCount < fabRowCount || trimRowCount < packRowCount) {
        $('.trim').first().clone(true).appendTo($(".service").last())
    } else {
        if (trimRowCount % 2 == 0) {
            var serviceRow = "<div style='background-color: #dddddd;' class='row service'></div>"
        } else {
            var serviceRow = "<div class='row service'></div>"
        }

        $(".card-body").append(serviceRow)
        $('.trim').first().clone(true).appendTo($(".service").last())
    }

    trimRowCount = trimRowCount + 1

})

$('#addPack').click(function () {
    if (packRowCount < fabRowCount || packRowCount < trimRowCount) {
        $('.pack').first().clone(true).appendTo($(".service").last())
    } else {

        if (packRowCount % 2 == 0) {
            var serviceRow = "<div style='background-color: #dddddd;' class='row service'></div>"
        } else {
            var serviceRow = "<div class='row service'></div>"
        }

        $(".card-body").append(serviceRow)
        $('.pack').first().clone(true).appendTo($(".service").last())
    }

    packRowCount = packRowCount + 1

})