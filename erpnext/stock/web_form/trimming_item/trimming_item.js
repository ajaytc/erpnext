var officialSuppliers = []

frappe.ready(function () {
	// bind events here

	setTimeout(() => {
		$('.card').css("width","200%")
	}, 200);

	window.onload = function () {

		setTimeout(() => {
			let input_element = document.querySelector('input[data-fieldname="trimming_vendor"]')
			getOfficialSuppliers()
			$(input_element).click(function () {
				setBadge(officialSuppliers)
			})

		}, 1000)


		// input_element.addEventListener("keyup",async function(e){
		// 	setBadge()
		// }
	}
})


function getOfficialSuppliers() {

	frappe.call({
		method: 'erpnext.modehero.supplier.get_official_supplier_list',
		args: {
			group: 'trimming'
		},
		callback: function (r) {
			if ((!r.exc)) {
				officialSuppliers = r.message

			}

		}
	})



}

function setBadge(officialSuppliers) {
	setTimeout(function () {
		$('#awesomplete_list_1').find("strong").each(function () {
			if (officialSuppliers.includes($(this).html())) {
				$(this).append("<svg style='padding-left:4px' width='1.1em' height='1.1em' viewBox='0 0 17 17' class='bi bi-check-circle' fill='currentColor' xmlns='http://www.w3.org/2000/svg'><path fill-rule='evenodd' d='M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z'/><path fill-rule='evenodd' d='M10.97 4.97a.75.75 0 0 1 1.071 1.05l-3.992 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.236.236 0 0 1 .02-.022z'/></svg>")
			}
		})
	}, 350)
	// setTimeout(function () {

	// },350)
	// $('#awesomplete_list_1').find("strong").each(function () {
	// 	if (officialSuppliers.includes($(this).html())) {
	// 		$(this).append("ders")
	// 	}
	// })
}
