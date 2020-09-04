frappe.ready(function () {
	// bind events here

	// $('div[data-fieldname="product_order_id"]').load(function() {
	// 	if("{{frappe.form_dict.name}}"!=null){
	// 		$('div[data-fieldname="product_order_id"]').css("display","none")

	// 	}
	// });

	setTimeout(
		function () {
			var el = {{ frappe.form_dict }}
			elProp = el[Object.keys(el)[0]]

			if (elProp != 1) {
				$('div[data-fieldname="product_order_id"]').css("display", "none")
				
			}
			if ({{f}}==1){
				$('div[data-fieldname="internal_ref_prod_order"]').css("display", "none")
			}

		}, 400
	)	
	

})



