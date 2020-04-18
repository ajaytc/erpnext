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

    createOrder(product, qtys)
})

function createOrder(product, qtys) {
    frappe.call({
        method: 'erpnext.modehero.production.create_production_order',
        args: {
            data: {
                product_category: $('#category>option:selected').text(),
                internal_ref: $('#internal-ref').val(),
                product_name: product,
                quantity: qtys,
                fabric_ref: $('#fabric-ref>option:selected').text(),
                production_factory: $('#factory>option:selected').text(),
                trimming_item: $('#trimming>option:selected').text(),
                packaging_item: $('#packaging>option:selected').text(),
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
