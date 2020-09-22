$(".grid-add-row").click(function () {

    // var markup = "<tr class='price_row'><td><input type='checkbox' class='checkRec'></td><td><input name='from' type='text' class='input-with-feedback form-control bold in  put-sm' placeholder='From'></td><td><input name='to' type='text' class='input-with-feedback form-control bold in  put-sm' placeholder='To'></td><td><input name='price' type='text' class='input-with-feedback form-control bold in  put-sm' placeholder='Price'></td></tr>";
    // $("table tbody").append(markup);
    $('.price_row').first().clone(true).appendTo($("tbody"))
    $('.price_row').last().find('input').val('')

});

// Find and remove selected table rows
$(".grid-remove-rows").click(function () {
    if(($("table tbody").find('input[class="checkRec"]:checked').length)<($("table tbody").find('input[class="checkRec"]')).length){
        $("table tbody").find('input[class="checkRec"]').each(function () {
            if ($(this).is(":checked")) {
                $(this).parents("tr").remove();
                $('#del_row').css("display","none")
            }
        });
    }
    
});

$('.checkRec').change(function () {
    if(($("table tbody").find('input[class="checkRec"]:checked').length)<($("table tbody").find('input[class="checkRec"]')).length){
        checkedR=$('.checkRec').is(':checked'); 
        if (checkedR) {
            $('#del_row').css("display","block")
        }else{
            $('#del_row').css("display","none")
        }
    }else{
        $('#del_row').css("display","none")
    }
   
});



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

                el.closest('.row').find('#fab_ref_list').append((`<option value="${value.name}"> 
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

                el.closest('.row').find('#trim_ref_list').append((`<option value="${value.name}"> 
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

                el.closest('.row').find('#pack_ref_list').append((`<option value="${value.name}"> 
                                       ${value.name} 
                                  </option>`));
            });

        }
    })
})


$('.addFab').click(function () {
    cloneOb=$('.fab-block').first().clone(true)
    cloneOb.find('input').val('')
    cloneOb.find('select').val('')
    cloneOb.appendTo(".fab")
    
})

$('.delFab').click(function () {
    $(this).parent().remove()
 
})
$('.delTrim').click(function () {
    $(this).parent().remove()
    
})

$('.delPack').click(function () {
    $(this).parent().remove()
    
})

$('.addTrim').click(function () {
    cloneOb=$('.trim-block').first().clone(true)
    cloneOb.find('input').val('')
    cloneOb.find('select').val('')
    cloneOb.appendTo(".trim")
    
})


$('.addPack').click(function () {
    cloneOb=$('.pack-block').first().clone(true)
    cloneOb.find('input').val('')
    cloneOb.find('select').val('')
    cloneOb.appendTo(".pack")
    
})

$("#productSubmit").click(function () {
    let files = ["tech_pack", "picture", "pattern", "barcode"];

    Promise.all(
        files.map((f) => {
            return checkFileUpload(f);
        })
    )
        .then((files) => {
            console.log(files);
            submitProdItem(files);
        })
        .catch((e) => {
            frappe.throw(e);
        });
});


function checkFileUpload(componentId) {
    return new Promise((resolve, reject) => {
        let file = $(`#${componentId}`).prop("files")[0];
        switch (componentId) {
            case "tech_pack":
                if (!file) {
                    console.log("Tech pack must upload");
                    resolve()

                } else {
                    uploadFile(componentId).then((res) => resolve(res));
                }

                break;
            case "picture":
                if (!file) {
                    console.log("Picture must upload");
                    resolve()
                } else {
                    uploadFile(componentId).then((res) => resolve(res));
                }
                break;
            case "pattern":
                if (!file) {
                    console.log("Pattern must upload");
                    resolve()
                } else {
                    uploadFile(componentId).then((res) => resolve(res));
                }

                break;
            case "barcode":
                if (!file) {
                    console.log("Barcode must upload");
                    resolve()

                } else {
                    uploadFile(componentId).then((res) => resolve(res));
                }

                break;
        }

    });
}

function submitProdItem(files) {

    prices = {}
    fab_suppliers = {}
    trim_suppliers = {}
    pack_suppliers = {}
    avg_price=0
    noConsumption=0

    // production price 

    if (!($('#prod_witout_size').is(':checked'))){
        sizing=$("#sizing").val()
    }else{
        sizing=null
    }

    $('.price_row').map(function () {
        let from = $(this).find("input[name='from']").val()
        let to = $(this).find("input[name='to']").val()
        let price = $(this).find("input[name='price']").val()

        prices[price] = {
            from: from,
            to: to,
            price: price
        }

    })

    avg_price=$('#avg_price').val()



    
    // suppliers

    // $('.service').map(function () {

    //     // fabric suppliers
    //     let fabric_supplier = $(this).find("select[name='fabric_sup']").val()
    //     let fabric_ref = $(this).find("select[name='fabric_ref']").val()
    //     let fabric_con = $(this).find("input[name='fabric_con']").val()

    //     fab_suppliers[Math.random()] = {
    //         fabric_supplier: fabric_supplier,
    //         fabric_ref: fabric_ref,
    //         fabric_con: fabric_con
    //     }

    //     // trimming suppliers
    //     let trim_supplier = $(this).find("select[name='trimming_sup']").val()
    //     let trim_ref = $(this).find("select[name='trimming_ref']").val()
    //     let trim_con = $(this).find("input[name='trimming_con']").val()

    //     trim_suppliers[Math.random()] = {
    //         trim_supplier: trim_supplier,
    //         trim_ref: trim_ref,
    //         trim_con: trim_con
    //     }

    //     // packaging suppliers
    //     let pack_supplier = $(this).find("select[name='packaging_sup']").val()
    //     let pack_ref = $(this).find("select[name='packaging_ref']").val()
    //     let pack_con = $(this).find("input[name='packaging_con']").val()

    //     pack_suppliers[Math.random()] = {
    //         pack_supplier: pack_supplier,
    //         pack_ref: pack_ref,
    //         pack_con: pack_con
    //     }

    $('.fab .fab-block').map(function () {
        let fabric_supplier = $(this).find("select[name='fabric_sup']").val()
        let fabric_ref = $(this).find("select[name='fabric_ref']").val()
        let fabric_con = $(this).find("input[name='fabric_con']").val()

        fab_suppliers[Math.random()] = {
            fabric_supplier: fabric_supplier,
            fabric_ref: fabric_ref,
            fabric_con: fabric_con
        }
        
    })

    $('.trim .trim-block').map(function () {
        let trim_supplier = $(this).find("select[name='trimming_sup']").val()
        let trim_ref = $(this).find("select[name='trimming_ref']").val()
        let trim_con = $(this).find("input[name='trimming_con']").val()

        trim_suppliers[Math.random()] = {
            trim_supplier: trim_supplier,
            trim_ref: trim_ref,
            trim_con: trim_con
        }
        
    })

    $('.pack .pack-block').map(function () {
        let pack_supplier = $(this).find("select[name='packaging_sup']").val()
        let pack_ref = $(this).find("select[name='packaging_ref']").val()
        let pack_con = $(this).find("input[name='packaging_con']").val()

        pack_suppliers[Math.random()] = {
            pack_supplier: pack_supplier,
            pack_ref: pack_ref,
            pack_con: pack_con
        }
        
    })



    // })




    console.log(prices)
    console.log(fab_suppliers)
    console.log(trim_suppliers)
    console.log(pack_suppliers)

    frappe.call({
        method: "erpnext.modehero.product.update_product_item",
        args: {
            data: {
                // order: "{{frappe.form_dict.order}}",
                item_name: $("#product_name").val(),
                item_group: $("#product_catagory").val(),
                item_code:$("#product_name").attr('data-name'),
                sizing:sizing,
                avg_price:avg_price,
                prices: prices,
                fab_suppliers: fab_suppliers,
                trim_suppliers: trim_suppliers,
                pack_suppliers: pack_suppliers,
                tech_pack: files[0],
                picture: files[1],
                pattern: files[2],
                barcode: files[3]
            }
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r);
                frappe.msgprint({
                    title: __("Notification"),
                    indicator: "green",
                    message: __("Product Created Successfully"),
                });
                window.location.replace("/product-item-list");
            } else {
                frappe.msgprint({
                    title: __("Notification"),
                    indicator: "red",
                    message: __("Product Creation Failed"),
                });
            }
        },
    });
}


function uploadFile(componentId) {
    return new Promise((resolve, reject) => {
        let file = $(`#${componentId}`).prop("files")[0];
        if (file.size / 1024 / 1024 > 5) {
            reject("Please upload file less than 5mb");
        }
        var reader = new FileReader();
        reader.readAsDataURL(file);
        console.log(file, reader, reader.result);
        reader.onload = function () {
            frappe.call({
                method: "frappe.handler.uploadfile",
                // method: 'erpnext.modehero.sales_order.upload_test',
                args: {
                    filename: file.name,
                    attached_to_doctype: "Production Order",
                    attached_to_field: componentId,
                    is_private: true,
                    filedata: reader.result,
                    from_form: true,
                },
                callback: function (r) {
                    if (!r.exc) {
                        console.log(r);
                        $(`#${componentId}-label`).html(r.message.file_url);
                        resolve(r.message.file_url);
                    }
                },
            });
        };
    });
}


$("#tech_pack").change(function () {
    $("#tech_pack-label").html($(this).prop("files")[0].name);
});

$("#picture").change(function () {
    $("#picture-label").html($(this).prop("files")[0].name);
});

$("#pattern").change(function () {
    $("#pattern-label").html($(this).prop("files")[0].name);
});

$("#barcode").change(function () {
    $("#barcode-label").html($(this).prop("files")[0].name);
});


$('#prod_witout_size').change(function () {
    // $('#delivered').prop('disabled', false)
    checked=$('#prod_witout_size').is(':checked'); 
    if(checked){
        $('#sizing').prop('disabled', true)
        // $("#price_div *").prop("disabled",true);
    }else{
        $('#sizing').prop('disabled', false)
        // $('#price_div *').prop("disabled",false);
    }
})



