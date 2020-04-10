$(document).ready(function () {
    $('.delete').click((e) => {
        console.log($(e.target).parent().parent())
    })
})

const fetchSizesCallback = (e) => {
    console.log('.....')
    // console.log($(e.target).parent().parent().parent().parent().find('.table-section')[0])
    product = $(e.target).find("option:selected").text()

    frappe.call({
        method: 'erpnext.modehero.quantity_per_size.getQuantities',
        args: {
            item: product
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r.message.quantities)
                let table = generateQuantityTables(r.message.quantities)
                console.log(table)
                $('#tables').html(table)
            }
        }
    });
}

$('#product').change(fetchSizesCallback)

function generateQuantityTables(quantities) {

    let tables = ''

    for (let i in quantities) {
        let heads = '', inputs = ''
        quantities[i].map(j => {
            console.log(j)
            heads += `<th scope="col">${j[2]}</th>`
            inputs += `<td><input type="text" class="form-control"></td>`
        })
        tables += generateTable(heads, inputs, i)
    }
    return tables
}

function generateTable(heads, inputs, order) {
    return `${order}
            <table class="table table-bordered">
                <tbody>
                    <tr class="qty">
                        <th scope="row">{{_("Quantity")}}</th>
                        ${heads}
                    </tr>
                    <tr class="modified-qty">
                        <th scope="row">{{_("Modified quantity")}}</th>
                        ${inputs}
                    </tr>
                </tbody>
            </table>
    `
}
