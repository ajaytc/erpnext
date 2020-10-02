var tablecount = 1;
var profoma = null;
var numeric = /^\d+$/;

$('.close').click(e => console.log($(e.target).parent()))
var fabRowCount = '';
var trimRowCount = '';
var packRowCount = '';

var fabCount = ''
var trimCount = ''
var packCount = ''

function clearNResetFields() {
    $('.extra').remove()

    $('#fab_supplier_list').val('')
    $('#fab_ref_list').val('')
    $('#fabric-consumption').val('')

    $('#trim_supplier_list').val('')
    $('#trim_ref_list').val('')
    $('#trimming-consumption').val('')

    $('#pack_supplier_list').val('')
    $('#pack_ref_list').val('')
    $('#packaging-consumption').val('')

    $('#fabric-status').prop("disabled", false);
    $('#trimming-status').prop("disabled", false);
    $('#packaging-status').prop("disabled", false);

    fabRowCount = 1;
    trimRowCount = 1;
    packRowCount = 1;
}


function getSupplierDetails(product) {
    clearNResetFields()
    fabCount = 0
    trimCount = 0
    packCount = 0
    frappe.call({
        method: 'erpnext.modehero.product.get_product_item',
        args: {
            product: product
        },
        callback: function (r) {
            if (!r.exc) {
                renderSuppliers(r.message)
            }
        }
    })
}

noOfsuppliers = 0

function renderSuppliers(r) {
    console.log(r.supplier)
    suppliers = r.supplier
    for (supplier in suppliers) {
        if (suppliers[supplier].supplier_group == 'Fabric') {
            if (fabCount == 0) {
                $('#fab_supplier_list').val(suppliers[supplier].supplier)
                $('#fab_ref_list').val(suppliers[supplier].fabric_ref)
                $('#fabric-consumption').val(suppliers[supplier].fabric_consumption)
                fabCount = fabCount + 1

            } else {
                addFab()
                $('.fab:eq(' + fabCount + ')').find('#fab_supplier_list').val(suppliers[supplier].supplier)
                $('.fab:eq(' + fabCount + ')').find('#fab_ref_list').val((suppliers[supplier].fabric_ref))
                $('.fab:eq(' + fabCount + ')').find('#fabric-consumption').val((suppliers[supplier].fabric_consumption))
                fabCount = fabCount + 1



            }
        }
        else if (suppliers[supplier].supplier_group == 'Trimming') {
            if (trimCount == 0) {
                $('#trim_supplier_list').val(suppliers[supplier].supplier)
                $('#trim_ref_list').val(suppliers[supplier].trimming_ref)
                $('#trimming-consumption').val(suppliers[supplier].trimming_consumption)
                trimCount = trimCount + 1


            } else {
                addTrim()
                $('.trim:eq(' + trimCount + ')').find('#trim_supplier_list').val(suppliers[supplier].supplier)
                $('.trim:eq(' + trimCount + ')').find('#trim_ref_list').val((suppliers[supplier].trimming_ref))
                $('.trim:eq(' + trimCount + ')').find('#trimming-consumption').val((suppliers[supplier].trimming_consumption))
                trimCount = trimCount + 1
            }
        }
        else if (suppliers[supplier].supplier_group == 'Packaging') {
            if (packCount == 0) {
                $('#pack_supplier_list').val(suppliers[supplier].supplier)
                $('#pack_ref_list').val(suppliers[supplier].packaging_ref)
                $('#packaging-consumption').val(suppliers[supplier].packaging_consumption)
                packCount = packCount + 1
            } else {
                addPack()
                $('.pack:eq(' + packCount + ')').find('#pack_supplier_list').val(suppliers[supplier].supplier)
                $('.pack:eq(' + packCount + ')').find('#pack_ref_list').val((suppliers[supplier].packaging_ref))
                $('.pack:eq(' + packCount + ')').find('#packaging-consumption').val((suppliers[supplier].packaging_consumption))
                packCount = packCount + 1
            }
        }

    }

    if(fabCount==0){
        $('#fabric-status').prop("disabled", true);
    }else{
        $('#fabric-status').prop("disabled", false);
    }
    if(trimCount==0){
        $('#trimming-status').prop("disabled", true);
    }else{
        $('#trimming-status').prop("disabled", false);
    }
    if(packCount==0){
        $('#packaging-status').prop("disabled", true);
    }else{
        $('#packaging-status').prop("disabled", false);
    }


}

const productUpdateCallback = (e) => {
    // console.log($(e.target).parent().parent().parent().parent().find('.table-section')[0])
    product = $(e.target).find("option:selected").val()
    $(e.target).closest('.product-table').attr('id', product)
    frappe.call({
        method: 'erpnext.stock.sizing.getSizes',
        args: {
            item: product
        },
        callback: function (r) {
            if (!r.exc) {
                let table = generateSizingTable(r.message.sizes)
                // console.log(table)
                $(e.target).parent().parent().parent().parent().parent().parent().parent().find('.table-section').html(table)
                $('.qty>td>input').change(priceUpdateCallback)
                getSupplierDetails($('#product').find('option:selected').val())
            }
        }
    });
}

function priceUpdateCallback(e) {
    // console.log(e.target.value, $(e.target).attr('data-size'))
    if (!numeric.test(e.target.value)) {
        $(e.target).css('border-color', 'red')
    } else {

        let products = {}
        let totalqty = 0

        //calculate price 
        $('#product-table').map(function () {
            let product = $(this).find('.selected-product>option:selected').text()

            $(this).find('.qty>td').map(function () {
                let qty = $(this).find('input').val()
                let size = $(this).find('input').attr('data-size')

                if (!products[product]) {
                    products[product] = {}
                }
                if (qty != '') {
                    products[product][size] = qty
                    totalqty += parseInt(qty)
                }
            })

        })

        $(e.target).css('border', '1px solid #ced4da')

        //getting fabric status
        let item = $('#fabric_list2').find('option:selected').text()
        let consumption = parseInt($('#fabric-consumption').val())
        console.log(totalqty, consumption)

        getStatus(item, consumption * totalqty).then(status => {
            $('#fabric-status').html(status)
        })


        // item = $('#trimming-status').find('option:selected').text()
        // consumption = parseInt($('#trimming-consumption').val())

        // getStatus(item, consumption * totalqty).then(status => {
        //     $('#trimming-status').html(status)
        // })
    }
}

$('#product').change(productUpdateCallback)
// $('#product').trigger('click');

function generateSizingTable(sizes) {

    let heads = '', inputs = ''

    sizes.map(s => {
        heads += `<th class="sizing" scope="col">${s}</th>`
        inputs += `<td><input type="text" data-size="${s}" class="form-control"></td>`
    })

    return `
            <table class="table table-bordered" id="product-table">
                <thead>
                    <tr>
                        <th scope="col">{{_("Sizing")}}</th>
                        ${heads}
                    </tr>
                </thead>
                <tbody>
                    <tr class="qty">
                        <th class="qty" scope="row">{{_("Quantity")}}</th>
                        ${inputs}
                    </tr>
                </tbody>
            </table>
    `
}

const cleartable = () => $('.table-section').html('')

function generateOptions(values) {
    let html = `<option value="">--+--</option>`
    values.map(v => {
        html += `<option value="${v.name}">${v.item_name}</option>`
    })
    return html
}

$('#category_list').change(function () {
    let category = $(this).find('option:selected').text()
    frappe.call({
        method: 'erpnext.modehero.product.get_products_of_category',
        args: {
            category
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r.message)
                $('#product').html(generateOptions(r.message))
            }
        }
    })
})

$('#submit').click(() => {
    let allnull = true

    let product = $('#product').find('option:selected').val()

    let qtys = []
    let sizes = []
    let counter = 0

    $('.sizing').map(function () {
        sizes.push($(this).text())
    })

    $('.qty>td>input').map(function () {
        if ($(this).val() != "") {
            allnull = false
            qtys.push({
                size: sizes[counter++],
                quantity: $(this).val()
            })
        }
        // qtys.push($(this).val())
    })

    console.log(product, qtys)
    if (allnull) {
        frappe.throw(frappe._("Please fill quantities"))
    }

    createOrder(product, qtys)
})

function createOrder(product, qtys) {
    fab_suppliers = {}
    trim_suppliers = {}
    pack_suppliers = {}

    $('.service').map(function () {

        // fabric suppliers
        $(this).find(".fab").map(function(){
            let fabric_supplier = $(this).find("input[id='fab_supplier_list']").val()
            let fabric_ref = $(this).find("input[id='fab_ref_list']").val()
            let fabric_con = $(this).find("input[id='fabric-consumption']").val()
            let fabric_status = $(this).find("select[id='fabric-status']").val()
    
            fab_suppliers[Math.random()] = {
                fabric_supplier: fabric_supplier,
                fabric_ref: fabric_ref,
                fabric_con: fabric_con,
                fabric_status: fabric_status
            }
        })
        

        // trimming suppliers
        $(this).find(".trim").map(function(){
            let trim_supplier = $(this).find("input[id='trim_supplier_list']").val()
            let trim_ref = $(this).find("input[id='trim_ref_list']").val()
            let trim_con = $(this).find("input[id='trimming-consumption']").val()
            let trim_status = $(this).find("select[id='trimming-status']").val()
    
            trim_suppliers[Math.random()] = {
                trim_supplier: trim_supplier,
                trim_ref: trim_ref,
                trim_con: trim_con,
                trim_status: trim_status
    
            }
        })
        

        // packaging suppliers
        $(this).find(".pack").map(function(){
            let pack_supplier = $(this).find("input[id='pack_supplier_list']").val()
            let pack_ref = $(this).find("input[id='pack_ref_list']").val()
            let pack_con = $(this).find("input[id='packaging-consumption']").val()
            let pack_status = $(this).find("select[id='packaging-status']").val()
    
            pack_suppliers[Math.random()] = {
                pack_supplier: pack_supplier,
                pack_ref: pack_ref,
                pack_con: pack_con,
                pack_status: pack_status
            }
        })

        



    })





    console.log(fab_suppliers)
    console.log(trim_suppliers)
    console.log(pack_suppliers)

    frappe.call({
        method: 'erpnext.modehero.production.create_production_order',
        args: {
            data: {
                product_category: $('#category_list>option:selected').val(),
                internal_ref: $('#internal-ref').val(),
                product_name: product,
                production_factory: $('#factory_list>option:selected').val(),
                final_destination:$('#destination_list>option:selected').val(),
                destination_type:$('#destination_list>option:selected').attr('data-type'),
                quantity: qtys,
                fab_suppliers: fab_suppliers,
                trim_suppliers: trim_suppliers,
                pack_suppliers: pack_suppliers,
                comment: $('#comment').val(),
            }
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
                let order = r.message.order
                if (order && order.name) {
                    frappe.msgprint({
                        title: __('Notification'),
                        indicator: 'green',
                        message: __('Production order ' + order.name + ' created successfully')
                    });
                }
                $('input').each(function () {
                    $(this).val("")
                });
                $('select').each(function () {
                    $(this).val("")
                });
                location.reload();
            }
        }
    })
}

function getStatus(item, requiredQuantity) {
    return new Promise((resolve, reject) => {
        frappe.call({
            method: 'erpnext.modehero.stock.get_status',
            args: {
                item,
                requiredQuantity
            },
            callback: function (r) {
                if (!r.exc) {
                    console.log(r)
                    resolve(r.message.status)
                }
            }
        })
    })
}

$('#fab_supplier_list').change(function () {
    let supplier = $(this).find('option:selected').text()
    frappe.call({
        method: 'erpnext.modehero.fabric.get_fabric',
        args: {
            vendor: supplier
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r.message)
                res = {
                    name: r.message.name,
                    item_name: r.message.fabric_ref
                }
                $('#fabric_list').html(generateOptions(res))
            }
        }
    })
})




$('#addFab').click(function () {
    addFab()

})

function addFab() {
    if ((fabRowCount + trimRowCount + packRowCount)%3!=0) {
        $('.fab').first().clone(true).appendTo($(".service").last())
    } else {
        if (fabRowCount % 2 == 0) {
            var serviceRow = "<div style='padding-top:3%' class='row service extra'></div>"
        } else {
            var serviceRow = "<div class='row service extra' style='padding-top:3%'></div>"
        }

        $(".card-body").append(serviceRow)
        $('.fab').first().clone(true).appendTo($(".service").last())
    }

    fabRowCount = fabRowCount + 1
}

$('#addTrim').click(function () {
    addTrim()


})

function addTrim() {
    if ((fabRowCount + trimRowCount + packRowCount)%3!=0) {
        $('.trim').first().clone(true).appendTo($(".service").last())
    } else {
        if (trimRowCount % 2 == 0) {
            var serviceRow = "<div style='padding-top:3%' class='row service extra'></div>"
        } else {
            var serviceRow = "<div class='row service extra' style='padding-top:3%'></div>"
        }

        $(".card-body").append(serviceRow)
        $('.trim').first().clone(true).appendTo($(".service").last())
    }

    trimRowCount = trimRowCount + 1
}

$('#addPack').click(function () {
    addPack()

})

function addPack() {
    if ((fabRowCount + trimRowCount + packRowCount)%3!=0) {
        $('.pack').first().clone(true).appendTo($(".service").last())
    } else {
        if (packRowCount % 2 == 0) {
            var serviceRow = "<div style='padding-top:3%' class='row service extra'></div>"
        } else {
            var serviceRow = "<div class='row service extra' style='padding-top:3%'></div>"
        }

        $(".card-body").append(serviceRow)
        $('.pack').first().clone(true).appendTo($(".service").last())
    }

    packRowCount = packRowCount + 1
}

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

