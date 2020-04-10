var tablecount = 1;

$('#addtable').click(() => {
    $('#box0').clone().addClass('class', 'product-table').appendTo('#container')
    tablecount++
    $('.selected-product').change(productUpdateCallback)
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
            }
        }
    });
}

$('.selected-product').change(productUpdateCallback)

function generateSizingTable(sizes) {

    let heads = '', inputs = ''

    sizes.map(s => {
        heads += `<th scope="col">${s}</th>`
        inputs += `<td><input type="text" class="form-control"></td>`
    })

    return `
            <table class="table table-bordered">
                <thead>
                    <tr class="sizing">
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



$('#validate').click(() => {
    let products = []
    let garmentlabel = $('#garmentlabel>option:selected').text()
    $('.product-table').map(function () {
        let product = $($(this).find('.selected-product')[0]).find('option:selected').text()
        let destination = $($(this).find('.destination')[0]).find('option:selected').text()

        let qtys = []
        $(this).find('.qty>td>input').map(function () {
            qtys.push($(this).val())
        })

        products.push({
            item: product,
            destination,
            quantities: qtys
        })
    })

    console.log(products, garmentlabel)
    frappe.call({
        method: 'erpnext.modehero.sales_order.create_sales_order',
        args: {
            items: products,
            garmentlabel
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
                frappe.msgprint({
                    title: __('Notification'),
                    indicator: 'green',
                    message: __('Sales order created successfully')
                });
            }
        }
    })

})