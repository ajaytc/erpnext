$('#users').click(function(){
    frappe.call({
        method: 'erpnext.modehero.user.test_deactivate',
        args: {},
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
            }
        }
    })
})