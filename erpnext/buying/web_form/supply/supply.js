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

	window.onload = function(){
		setTimeout(function(){
			let suppllier_name_keypress = ""
			let input_element = document.querySelector('input[data-fieldname="supplier_name"]')
			input_element.addEventListener("keyup",async function(e){
				suppllier_name_keypress = document.querySelector('input[data-fieldname="supplier_name"]').value
				let is_official = await autofill_disable_with_official_supplier(suppllier_name_keypress)
				if (!is_official){
					let input_elements = document.getElementsByTagName("input")
					for (let i=1;i<input_elements.length;i++){
						input_elements[i].disabled = false
					}
				}
			})
			input_element.addEventListener("focusout",function(e){
				frappe.web_form.set_value("supplier_name", suppllier_name_keypress)
			})
			input_element.addEventListener("awesomplete-selectcomplete",async function(e){
				suppllier_name_keypress = document.querySelector('input[data-fieldname="supplier_name"]').value
				frappe.web_form.set_value("supplier_name", suppllier_name_keypress)
				let is_official = await autofill_disable_with_official_supplier(suppllier_name_keypress)
				if (!is_official){
					let input_elements = document.getElementsByTagName("input")
					for (let i=1;i<input_elements.length;i++){
						input_elements[i].disabled = false
					}
				}
			})
		},1000)
	}

})


async function  autofill_disable_with_official_supplier(official_sup_name){
	var is_this_official= false
	await frappe.call({
        method: 'erpnext.modehero.supplier.get_official_supplier_data',
        args: {
            supplier_name:official_sup_name
        },
        callback: function (r) {
            if ((!r.exc) && (r.message['status'] == "ok")) {
				let fields = ["name","contact","email","address1","adress2","phone","city","country","zip_code","tax_id","supplier_group"]
				let data= r.message["data"]
				for (let i=0;i<fields.length;i++){
					frappe.web_form.set_value(fields[i], data[fields[i]])
				}
				let input_elements = document.getElementsByTagName("input")
				for (let i=1;i<input_elements.length;i++){
					input_elements[i].disabled = true
				}
				is_this_official = true
                return null
            }
            return null
        }
	});
	return is_this_official
}