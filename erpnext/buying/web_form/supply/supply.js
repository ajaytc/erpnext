frappe.ready(function () {
	// bind events here
	let type = "{{ type }}"
	console.log(type)
	frappe.web_form.after_load = () => {
		frappe.web_form.set_value('supplier_group', type)
	}
})