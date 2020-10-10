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
				setBadge()
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
			$(input_element).click(function () {
				setBadge()
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

function setBadge() {
	setTimeout(function () {
		$('#awesomplete_list_1').find("strong").each(function () {
			$(this).append("<svg style='padding-left:4px' width='1em' height='1em' viewBox='0 0 16 16' class='bi bi-patch-check' fill='currentColor' xmlns='http://www.w3.org/2000/svg'><path fill-rule='evenodd' d='M10.273 2.513l-.921-.944.715-.698.622.637.89-.011a2.89 2.89 0 0 1 2.924 2.924l-.01.89.636.622a2.89 2.89 0 0 1 0 4.134l-.637.622.011.89a2.89 2.89 0 0 1-2.924 2.924l-.89-.01-.622.636a2.89 2.89 0 0 1-4.134 0l-.622-.637-.89.011a2.89 2.89 0 0 1-2.924-2.924l.01-.89-.636-.622a2.89 2.89 0 0 1 0-4.134l.637-.622-.011-.89a2.89 2.89 0 0 1 2.924-2.924l.89.01.622-.636a2.89 2.89 0 0 1 4.134 0l-.715.698a1.89 1.89 0 0 0-2.704 0l-.92.944-1.32-.016a1.89 1.89 0 0 0-1.911 1.912l.016 1.318-.944.921a1.89 1.89 0 0 0 0 2.704l.944.92-.016 1.32a1.89 1.89 0 0 0 1.912 1.911l1.318-.016.921.944a1.89 1.89 0 0 0 2.704 0l.92-.944 1.32.016a1.89 1.89 0 0 0 1.911-1.912l-.016-1.318.944-.921a1.89 1.89 0 0 0 0-2.704l-.944-.92.016-1.32a1.89 1.89 0 0 0-1.912-1.911l-1.318.016z'/><path fill-rule='evenodd' d='M10.354 6.146a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708 0l-1.5-1.5a.5.5 0 1 1 .708-.708L7 8.793l2.646-2.647a.5.5 0 0 1 .708 0z'/></svg>")
		})
	},350)
	
	
}

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