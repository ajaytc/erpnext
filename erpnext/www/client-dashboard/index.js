$(document).ready(function () {
    $('.delete').click((e) => {
        let so = $(e.target).attr('order-no')
        // frappe.confirm('Are you sure you want to delete the sales order ' + so + ' ?',
        //     () => {
        //         // action to perform if Yes is selected

        //     }, () => {
        //         // action to perform if No is selected
        //     })
        let res = confirm('Are you sure you want to delete the sales order ' + so + ' ?');
        if (res) {
            frappe.call({
                method: 'erpnext.modehero.sales_order.delete',
                args: {
                    order: so
                },
                callback: function (r) {
                    if (!r.exc) {
                        console.log(r)
                        window.location.reload()
                    }
                }
            })
        } else {

        }
    })
})