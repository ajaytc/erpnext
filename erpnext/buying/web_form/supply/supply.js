frappe.ready(function () {
	// bind events here
	let type = "{{ type }}"
	setTimeout(() => {
		if (type == 'fabric') {
			frappe.web_form.set_value('supplier_group', 'Fabric')
		} else if (type == 'trimming') {
			frappe.web_form.set_value('supplier_group', 'Trimming')
		} else if (type == 'packaging') {
			frappe.web_form.set_value('supplier_group', 'Packaging')
		}
	}, 1000);

	setTimeout(() => {
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