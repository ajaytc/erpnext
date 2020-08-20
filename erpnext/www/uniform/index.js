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
                    <label>{{_("Name")}}</label>
                    <input class="form-control clientname-select" id="client-name-select">
                </div>`
                html=namePart
                $.each(products, function (index, value) {
                        html = html + `
                <div class="col-2" style="text-align: center;flex: 0 0 12.667%;padding-left:2%">
                    <label style="margin-top: 4%;">{{_("`+ value['prod_name'] + `")}}</label>
                    <div class="row">
                        <div class="col-4">
                            <label>{{_("Order#")}}</label>
                            <input class="form-control clientname-select" id="client-name-select">
                        </div>
                        <div class="col-4">
                            <label>{{_("Qty")}}</label>
                            <input class="form-control clientname-select" value="`+ value['qty'] + `" id="client-name-select">

                        </div>
                        <div class="col-4">
                            <label>{{_("Size")}}</label>
                            <input class="form-control clientname-select" id="client-name-select">

                        </div>
                    </div>

                </div>
                
                `
                    


                })
                $('.product').html('')
                $('#products').html(html)
            }
        }
    })
})

$('#addSegment').click(function () {
    $('#products').first().clone(true).appendTo($("#seg"))
})