frappe.ready(function () {
	console.log(frappe.web_form)
	// bind events here
	setTimeout(() => {
		frappe.call({
			method: 'erpnext.modehero.product.get_item_code',
			args: {},
			callback: function (r) {
				if (!r.exc) {
					console.log(r.message)
					frappe.web_form.set_value('item_code', r.message)
				}
			}
		});
		frappe.call({
			method: 'erpnext.modehero.user.get_brand',
			args: {
				user: frappe.session.user
			},
			callback: function (r) {
				if (!r.exc) {
					console.log(r.message)
					frappe.web_form.set_value('brand', r.message)
				}
			}
		});
	}, 500);
})