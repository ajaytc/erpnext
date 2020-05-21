var tablecount = 1;
var profoma = null;
var numeric = /^\d+$/;

$('.close').click(e => console.log($(e.target).parent()))

const productUpdateCallback = (e) => {
    // console.log($(e.target).parent().parent().parent().parent().find('.table-section')[0])
    product = $(e.target).find("option:selected").text()
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
                $(e.target).parent().parent().parent().parent().find('.table-section').html(table)
                $('.qty>td>input').change(priceUpdateCallback)
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
        let item = $('#fabric_list').find('option:selected').text()
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

$('#product').click(productUpdateCallback)
$('#product').trigger('click');

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
    let html = ''
    values.map(v => {
        html += `<option value="${v.name}">${v.item_name}</option>`
    })
    return html
}

$('#category').change(function () {
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
    frappe.call({
        method: 'erpnext.modehero.production.create_production_order',
        args: {
            data: {
                product_category: $('#category_list>option:selected').text(),
                internal_ref: $('#internal-ref').val(),
                product_name: product,
                quantity: qtys,
                fabric_ref: $('#fabric_list>option:selected').text(),
                fabric_consumption: $('#fabric-consumption').val(),
                production_factory: $('#factory_list>option:selected').text(),
                trimming_item: $('#trimming_list>option:selected').text(),
                trimming_consumption: $('#trimming-consumption').val(),
                packaging_item: $('#packaging_list>option:selected').text(),
                packaging_consumption: $('#packaging-consumption').val(),
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