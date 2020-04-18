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

$('#product').click(productUpdateCallback)

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


$('#validate').click(function () {
    let order = $('#order-no').text().trim()
    frappe.call({
        method: 'erpnext.modehero.sales_order.validate_order',
        args: {
            order
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)

            }
        }
    })
})

function priceUpdateCallback(e) {
    // console.log(e.target.value, $(e.target).attr('data-size'))
    if (!numeric.test(e.target.value)) {
        $(e.target).css('border-color', 'red')
    } else {

        let products = {}

        //calculate price 
        $('.product-table').map(function () {
            let product = $(this).find('#product>option:selected').text()

            $(this).find('.qty>td').map(function () {
                let qty = $(this).find('input').val()
                let size = $(this).find('input').attr('data-size')

                if (!products[product]) {
                    products[product] = {}
                }
                if (qty != '') {
                    products[product][size] = qty
                }
            })

        })
        console.log(products)

        $(e.target).css('border', '1px solid #ced4da')
        calculatePrice(products)
    }
}

function calculatePrice(products) {
    frappe.call({
        method: 'erpnext.modehero.sales_order.calculate_price',
        args: {
            products
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r.message)
                $('#total').html(r.message.total)
                let prices = r.message
                for (let p in prices) {
                    $(`#${p}`).find('.pricing-table .total-price').html(prices[p])
                    $(`#${p}`).find('.pricing-table .price-pp').html(prices.perpiece[p])
                    $(`#${p}`).find('.pricing-table .total-order').html(prices.total)
                }
            }
        }
    })
}

function calculatePriceOnLoad() {
    let products = {}
    $('.product-table').map(function () {
        let product = $(this).find('.product').html()
        $(this).find('.qty>td').map(function () {
            let qty = $(this).html().trim()
            let size = $(this).attr('data-size')

            if (!products[product]) {
                products[product] = {}
            }
            if (qty != '') {
                products[product][size] = qty
            }
        })
    })
    console.log(products)
    calculatePrice(products)
}

function generateOptions(values) {
    let html = ''
    values.map(v => {
        html += `<option value="${v.name}">${v.name}</option>`
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

    let product = $('#product').find('option:selected').text()

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

    let techpack = '', picture = '', pattern = ''
    let files = ['techpack', 'picture', 'pattern']

    Promise.all(files.map(f => {
        if ($(`#${f}`).prop('files')[0]) {
            return uploadFile(f)
        } else {
            return ''
        }
    })).then(files => {
        console.log(files)
        createOrder(product, qtys, files[0], files[1], files[2])
    }).catch(e => {
        frappe.throw(e)
    })

})

function createOrder(product, qtys, techpack, pattern, picture) {
    frappe.call({
        method: 'erpnext.modehero.prototype.create_prototype_order',
        args: {
            data: {
                internal_ref: $('#internal-ref').val(),
                techpack,
                pattern,
                picture,
                comment: $('#comment').val(),
                consumption: $('#fabric-consumption').val(),
                product_category: $('#category>option:selected').text(),
                fabric_ref: $('#fabric-ref>option:selected').text(),
                product,
                destination: $('#destination').find('option:selected').text(),
                trimming_item: $('#trimming>option:selected').text(),
                production_factory: $('#factory>option:selected').text(),
                quantity: qtys,
                price: $('#price').val()
            }
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
                let order = r.message.order
                if (order && order.name) {
                    // frappe.msgprint({
                    //     title: __('Notification'),
                    //     indicator: 'green',
                    //     message: __('Sales order ' + order.name + ' created successfully')
                    // });
                }
            }
        }
    })
}

function uploadFile(componentId) {
    return new Promise((resolve, reject) => {
        let file = $(`#${componentId}`).prop('files')[0]
        if (file.size / 1024 / 1024 > 5) {
            reject("Please upload file less than 5mb")
        }
        var reader = new FileReader();
        reader.readAsDataURL(file);
        console.log(file, reader, reader.result)
        reader.onload = function () {
            frappe.call({
                method: 'frappe.handler.uploadfile',
                // method: 'erpnext.modehero.sales_order.upload_test',
                args: {
                    filename: file.name,
                    attached_to_doctype: 'Prototype Order',
                    attached_to_field: componentId,
                    is_private: true,
                    filedata: reader.result,
                    from_form: true,
                },
                callback: function (r) {
                    if (!r.exc) {
                        console.log(r)
                        $(`#${componentId}-label`).html(r.message.file_url)
                        resolve(r.message.file_url)
                    }
                }
            })

        }
    })

}
$('#techpack').change(function () {
    $('#techpack-label').html($(this).prop('files')[0].name)
})

$('#pattern').change(function () {
    $('#pattern-label').html($(this).prop('files')[0].name)
})

$('#picture').change(function () {
    $('#picture-label').html($(this).prop('files')[0].name)
})