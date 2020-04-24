frappe.ready(function() {
	// bind events here
	frappe.call({
		method: 'erpnext.modehero.user.get_brand',
		args: {
			user: frappe.session.user
		},
		callback: function (r) {
			if (!r.exc) {
				console.log(r.message)
				frappe.web_form.set_value('brand_name', r.message)
			}
		}
	});
})