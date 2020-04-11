var tablecount = 1;

$('#addtable').click(() => {
    $('#box0').clone().addClass('class', 'product-table').appendTo('#container')
    tablecount++
    $('.selected-product').click(productUpdateCallback)
    setClose()
})

$('.close').click(e => console.log($(e.target).parent()))

const productUpdateCallback = (e) => {
    // console.log($(e.target).parent().parent().parent().parent().find('.table-section')[0])
    product = $(e.target).find("option:selected").text()
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
                {% if isCustomer %}
                $('.modified-qty>td>input').attr('disabled', true)
                {% endif %}
            }
        }
    });
}

$('.selected-product').click(productUpdateCallback)

function generateSizingTable(sizes) {

    let heads = '', inputs = ''

    sizes.map(s => {
        heads += `<th class="sizing" scope="col">${s}</th>`
        inputs += `<td><input type="text" class="form-control"></td>`
    })

    return `
            <table class="table table-bordered">
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
                    <tr class="modified-qty">
                        <th scope="row">{{_("Modified quantity")}}</th>
                        ${inputs}
                    </tr>
                </tbody>
            </table>
    `
}

const cleartable = () => $('.table-section').html('')

const setClose = () => {
    $('.close').click(e => {
        if (tablecount > 1) {
            $(e.target).parent().parent().parent().remove()
            tablecount--
        }
    })
}

setClose()


$('#submit').click(() => {
    let products = {}
    let garmentlabel = $('#garmentlabel>option:selected').text()
    let allnull = true
    $('.product-table').map(function () {
        let product = $($(this).find('.selected-product')[0]).find('option:selected').text()
        let destination = $($(this).find('.destination')[0]).find('option:selected').text()

        let qtys = {}
        let sizes = []
        let counter = 0

        $(this).find('.sizing').map(function () {
            sizes.push($(this).text())
        })

        $(this).find('.qty>td>input').map(function () {
            if ($(this).val() != "") {
                allnull = false
            }
            // qtys.push($(this).val())
            qtys[sizes[counter++]] = $(this).val()
        })

        products[product] = {
            item: product,
            destination,
            quantities: qtys
        }
    })

    console.log(products, garmentlabel)
    if (allnull) {
        frappe.throw(frappe._("Please fill quantities"))
    }
    frappe.call({
        method: 'erpnext.modehero.sales_order.create_sales_order',
        args: {
            items: products,
            garmentlabel,
            internalref: $('#internal-ref').val()
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
                let order = r.message.order
                if (order && order.name) {
                    $('#order-no').html(order.name)
                    frappe.msgprint({
                        title: __('Notification'),
                        indicator: 'green',
                        message: __('Sales order ' + order.name + ' created successfully')
                    });
                }
            }
        }
    })

})