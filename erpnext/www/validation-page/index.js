$(document).ready(function () {
    $('.delete').click((e) => {
        console.log($(e.target).parent().parent())
    })
})

const productUpdateCallback = (e) => {
    // console.log($(e.target).parent().parent().parent().parent().find('.table-section')[0])
    product = $(e.target).find("option:selected").text()
    frappe.call({
        method: 'erpnext.modehero.quantity_per_size.getQuantities',
        args: {
            item: product
        },
        callback: function (r) {
            if (!r.exc) {
                let table = generateQuantityTable(r.message.quantities)
                // console.log(table)
                $(e.target).parent().parent().parent().parent().find('.table-section').html(table)
            }
        }
    });
}

function generateQuantityTable(quantities) {

    let heads = '', inputs = ''

    sizes.map(s => {
        heads += `<th scope="col">${s}</th>`
        inputs += `<td><input type="text" class="form-control"></td>`
    })

    return `
            <table class="table table-bordered">
                <tbody>
                    <tr class="qty">
                        <th scope="row">{{_("Quantity")}}</th>
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

