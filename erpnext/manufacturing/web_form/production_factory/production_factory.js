frappe.ready(function () {
	// bind events here
	window.onload = function(){
		setTimeout(function(){
			let factory_name_keypress = ""
			let input_element = document.querySelector('input[data-fieldname="factory_name"]')
			input_element.addEventListener("keyup",async function(e){
				factory_name_keypress = document.querySelector('input[data-fieldname="factory_name"]').value
				let is_official = await autofill_disable_with_official_factory(factory_name_keypress)
				console.log(is_official)
				if (!is_official){
					let input_elements = document.getElementsByTagName("input")
					for (let i=1;i<input_elements.length;i++){
						input_elements[i].disabled = false
					}
				}
			})
			input_element.addEventListener("focusout",function(e){
				frappe.web_form.set_value("factory_name", factory_name_keypress)
			})
			input_element.addEventListener("awesomplete-selectcomplete",async function(e){
				factory_name_keypress = document.querySelector('input[data-fieldname="factory_name"]').value
				frappe.web_form.set_value("factory_name", factory_name_keypress)
				let is_official = await autofill_disable_with_official_factory(factory_name_keypress)
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
async function  autofill_disable_with_official_factory(official_fac_name){
	var is_this_official= false
	await frappe.call({
        method: 'erpnext.modehero.factory.get_official_factory_data',
        args: {
            factory_name:official_fac_name
        },
        callback: function (r) {
            if ((!r.exc) && (r.message['status'] == "ok")) {
				let fields = ["factory_name","contact","email_address","address_line_1","address_line_2","phone","city_town","country","zip_code"]
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