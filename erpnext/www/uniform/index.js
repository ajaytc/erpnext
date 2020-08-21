function generateOptions(values, val_key, txt_key) {
    let html = ''
    html += `<option value="">---:---</option>`
    values.map(v => {
        html += `<option value="${v[val_key]}">${v[txt_key]}</option>`
    })
    return html
}

$('#client-name-select').change(function () {
    makePOSList($(this))
    makePackageList($(this))


})

function makePOSList(el) {
    let client = el.find('option:selected').val()
    frappe.call({
        method: 'erpnext.modehero.uniform.get_pos_of_client',
        args: {
            client
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r.message)
                $('#pos-select').html(generateOptions(r.message, 'name', 'point_of_sale'))
            }
        }
    })
}

function makePackageList(el) {
    let client = el.find('option:selected').val()
    frappe.call({
        method: 'erpnext.modehero.uniform.get_packages_of_client',
        args: {
            client
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r.message)
                $('#package-select').html(generateOptions(r.message, 'name', 'package_name'))
            }
        }
    })

}

$('#package-select').change(function () {
    let packageName = $(this).find('option:selected').val()
    frappe.call({
        method: 'erpnext.modehero.uniform.get_products_of_package',
        args: {
            packageName
        },
        callback: function (r) {
            if (!r.exc) {
                $('#uniformSubmit').show()
                $('#addSegment').show()
                console.log(r.message)
                products = r.message
                html = ``
                firstFlag = true
                namePart = `<div class="col-1" style="padding-top: 2.6%;">
                    <label>{{_("Name*")}}</label>
                    <input class="form-control clientname-select" id="client-name-select">
                </div>`
                html = namePart
                $.each(products, function (index, value) {
                    html = html + `
                <div class="col-2 seg-products" style="text-align: center;flex: 0 0 12.667%;padding-left:2%">
                    <label style="margin-top: 4%;">{{_("`+ value['item_name'] + `")}}</label><span style="text-align: right !important;padding-left:20px" id="com">
                    <a type="button" id="addFromStock" style="">+</a>
                </span><span><a type="button" class="dha"  style="padding-left:5px">!</a></span>
                <hr style="margin-top:0px;margin-bottom:0px">
                    <label style="margin-top: 4%;display:none" id="item_code">{{_("`+ value['item_code'] + `")}}</label>
                    <div class="row">
                        <div class="col-4">
                            <label>{{_("Order#*")}}</label>
                            <input class="form-control product-select" id="orderNum">
                        </div>
                        <div class="col-4">
                            <label>{{_("Qty*")}}</label>
                            <input class="form-control" disabled value="`+ value['qty'] + `" id="qty">

                        </div>
                        <div class="col-4">
                            <label>{{_("Size*")}}</label>
                            <input class="form-control product-select" id="size">

                        </div>
                    </div>
                    <div style="display: none;" id="commentdiv">
                            <label>{{_("Comment")}}</label>
                            <input type="text" class="form-control clientname-select" id="commentField">
                        </div>

                </div>
                
                `



                })
                $('.segmentPart').html('')
                $('#segment').html(html)
            }
        }
    })
})
$(document).ready(function(){
    $(document).on("click", "a.dha" , function() {
        if($(this).parent().parent().find('#commentdiv').is(":hidden")){
            $(this).parent().parent().find('#commentdiv').show()
        }else{
            $(this).parent().parent().find('#commentdiv').hide()
        }
        
    });
});
// $("a").on("click",".dha",function () {
//     $(this).find('#commentdiv').show()
// })
$('#addSegment').click(function () {
    $('#segment').first().clone(true).appendTo($("#segs"))
    addedSeg = $('.segmentPart').last()
    $(addedSeg).find('.product-select').val('')
    $(addedSeg).find('#client-name-select').val('')
    $(addedSeg).find('#commentdiv').hide()
    // $(addedSeg).find('#size').val('')



})

$('#uniformSubmit').click(function () {
    customer = $('#client-name-select').val()
    pos = $('#pos-select').val()
    packageName = $('#package-select').val()
    segments = []
    notCompleted = false


    $('.segmentPart').each(function (index, value) {
        console.log(value)
        name = $(value).find('#client-name-select').val()
        if (name == '') {
            notCompleted = true
            return giveError()

        }
        segment = {}
        segment['name'] = name
        segmentProducts = []
        $(value).find('.seg-products').each(function (index, value) {
            orderNum = $(value).find('#orderNum').val()
            qty = $(value).find('#qty').val()
            size = $(value).find('#size').val()
            comment=$(value).find('#commentField').val()
            item_code = $(value).find('#item_code').text()
            if (orderNum == '' || qty == '' || size == '') {
                notCompleted = true
                return giveError()

            }

            segmentProduct = {}
            segmentProduct['orderNum'] = orderNum
            segmentProduct['qty'] = qty
            segmentProduct['size'] = size
            segmentProduct['comment'] = comment
            segmentProduct['item_code'] = item_code

            segmentProducts.push(segmentProduct)

        })
        segment['segmentProducts'] = segmentProducts
        segments.push(segment)



    })

    if (!notCompleted) {
        frappe.call({
            method: 'erpnext.modehero.uniform.createUniformOrder',
            args: {
                data: {
                    'client': customer,
                    'pos': pos,
                    'package': packageName,
                    'segments': segments
                }
            },
            callback: function (r) {
                if (!r.exc) {
                    console.log(r.message)
                    frappe.msgprint({
                        title: __('Notification'),
                        indicator: 'green',
                        message: __('Uniform order created successfully')
                    });
                } else {
                    frappe.msgprint({
                        title: __('Notification'),
                        indicator: 'red',
                        message: __('Uniform order creation failed')
                    });
                }
            }
        })
    }






})

function giveError() {
    frappe.msgprint({
        title: __('Notification'),
        indicator: 'red',
        message: __('Please fill all mandetory fields')
    });

}