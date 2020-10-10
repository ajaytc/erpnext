frappe.ready(function () {
	// bind events here
	window.onload = function(){
		setTimeout(function(){
			let factory_name_keypress = ""
			let input_element = document.querySelector('input[data-fieldname="factory_name"]')
			input_element.addEventListener("keyup",async function(e){
				factory_name_keypress = document.querySelector('input[data-fieldname="factory_name"]').value
				let is_official = await autofill_disable_with_official_factory(factory_name_keypress)
				setBadge()
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
			$(input_element).click(function () {
				setBadge()
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

function setBadge() {
	setTimeout(function () {
		$('#awesomplete_list_1').find("strong").each(function () {
			$(this).append('<svg style="margin-left: 10px;" width="1.1em" height="1.1em" viewBox="0 0 17 17" class="bi bi-check-circle" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/><path fill-rule="evenodd" d="M10.97 4.97a.75.75 0 0 1 1.071 1.05l-3.992 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.236.236 0 0 1 .02-.022z"/></svg>')
		})
	},350)
}

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