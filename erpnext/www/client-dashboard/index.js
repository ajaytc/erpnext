$(document).ready(function () {
    $('.cancel').click((e) => {
        let so = $(e.target).attr('order-no')
        // frappe.confirm('Are you sure you want to delete the sales order ' + so + ' ?',
        //     () => {
        //         // action to perform if Yes is selected

        //     }, () => {
        //         // action to perform if No is selected
        //     })
        let res = confirm('Are you sure you want to delete the client purchase order ' + so + ' ?');
        if (res) {
            frappe.call({
                method: 'erpnext.modehero.sales_order.cancel',
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

$(document).ready(function () {
    $('.duplicate').click((e) => {
        let so = $(e.target).attr('order-no')
        let res = confirm('Are you sure you want to duplicate the client purchase order ' + so + ' ?');
        if (res) {
            frappe.call({
                method: 'erpnext.modehero.sales_order.duplicate',
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