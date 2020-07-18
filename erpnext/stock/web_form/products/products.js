frappe.ready(function () {
	// bind events here
	console.log(frappe.web_form)
	setTimeout(() => {
		if (frappe.web_form.is_new) {
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
		}
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



	setTimeout(() => {
		$('.col-lg-6').addClass('col-lg-10')
	}, 500);
})