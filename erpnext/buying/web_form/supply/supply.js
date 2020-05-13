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


})