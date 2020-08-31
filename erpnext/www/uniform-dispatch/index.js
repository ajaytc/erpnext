$(document).ready(function () {
    $('.segment').each(function (index, value) {
        if ($(value).find('.piecesCheck').length == $(value).find('.pieces').length) {
            $(value).find('#fullCheck').show()
        }

    })
});

$('.plGen').click(function () {
    packProductDetails = {}
    el = $(this)
    client = $(el).parent().parent().parent().find('#client').text()
    pos=$(el).parent().parent().parent().attr('data-pos')
    fullCheckedEls = $(el).parent().parent().parent().find('input[name="piecesCheck"]:checked')
    $(fullCheckedEls).each(function (index, pack) {
        reciever = $(pack).parent().parent().parent().find('#recieverName').text()
        if (!(reciever in packProductDetails)) {
            packProductDetails[reciever] = []
        }

        packProduct = $(pack).parent().parent()
        product = $(packProduct).find('.product').text()
        order_no = $(packProduct).find('#order_no').text()
        qty = $(packProduct).find('#qty').text()
        size = $(packProduct).find('#size').text()
        piece_name = $(packProduct).attr('data-piece')
        prodDetail = {}
        prodDetail['product'] = product
        prodDetail['size'] = size
        prodDetail['qty'] = qty
        prodDetail['name'] = piece_name

        packProductDetails[reciever].push(prodDetail)

        // packProducts=$(pack).parent().parent().parent().find('.pieces')
        // $(packProducts).each(function (index,packProduct) {


        // })


    })

    frappe.call({
        method: 'erpnext.modehero.uniform.generatePl',
        args: {
            data: {
                packProductDetails: packProductDetails,
                client: client,
                pos:pos
            }
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
                location.reload();

            } else {
                console.log(r)
            }
        }
    })
})

// $('#plGen').click(function () {
//     markBatchGeneration()
//     markIndividuals()


// })

$('.pl').click(function () {
    packListName = $(this).attr('data-packList')
    frappe.call({
        method: 'erpnext.modehero.uniform.displayPLDoc',
        args: {
            data: {
                packlist_name: packListName
            }
        },
        callback: function (r) {
            if (!r.exc) {
                html=r.message.content
                // html=$.parseHTML(htmlstr)
                html=html.replace('src="brandlogoimage"', "src="+r.message.brand_logo);
                // $(html).find('#brand_logo').attr("src",r.message.brand_logo)
                // $("#my_image").attr("src","second.jpg");
                render_pdf(html)

            } else {
                console.log(r)
            }
        }
    })

})
function render_pdf(html) {
    var formData = new FormData();

	//Push the HTML content into an element
    formData.append("html",html);
    // if (opts.orientation) {
	// 	formData.append("orientation", opts.orientation);
	// }
	var blob = new Blob([], { type: "text/xml"});
	formData.append("blob", blob);

    var xhr = new XMLHttpRequest();
    $("#container").css("opacity",0.5);
	xhr.open("POST", '/api/method/frappe.utils.print_format.report_to_pdf');
	xhr.setRequestHeader("X-Frappe-CSRF-Token", frappe.csrf_token);
    xhr.responseType = "arraybuffer";
    
	xhr.onload = function(success) {
		if (this.status === 200) {
            $("#container").css("opacity",1);
			var blob = new Blob([success.currentTarget.response], {type: "application/pdf"});
            var objectUrl = URL.createObjectURL(blob);
            window.open(objectUrl);
            // target=`<a href="${objectUrl}">${objectUrl}</a>`
            // $('#order_doc').html(target)

			
			//Open report in a new window
			// window.open(objectUrl);
        }
        else{
            frappe.msgprint({
              title: __("Notification"),
              indicator: "red",
              message: __(
                "Not Permitted"
              ),
            });
            $(".row").css("opacity",1);
          }
    };
    
    xhr.send(formData);
}

$('input[name="fullPack"]').change(function () {
    if (this.checked) {
        $(this).parent().parent().find('.piecesCheck').prop("checked", true);
    } else {
        $(this).parent().parent().find('.piecesCheck').prop("checked", false);
    }
});

function markBatchGeneration() {
    packProductDetails = {}
    el = $(this)
    fullCheckedEls = $(el).parent().find('input[name="fullPack"]:checked')
    $(fullCheckedEls).each(function (index, pack) {
        reciever = $(pack).parent().find('#recieverName').val()
        if (!(reciever in packProductDetails)) {
            packProductDetails[reciever] = []
        }

        packProducts = $(pack).parent().parent().find('.pieces')
        $(packProducts).each(function (index, packProduct) {
            product = $(packProduct).find('#product').val()
            order_no = $(packProduct).find('#order_no').val()
            qty = $(packProduct).find('#qty').val()
            size = $(packProduct).find('#size').val()
            prodDetail = {}
            prodDetail['product'] = product
            prodDetail['size'] = size
            prodDetail['qty'] = qty

            packProductDetails[reciever].push(prodDetail)

        })


    })
}

$('input[name="fullPack"]:checked').each(function () {
    selectedPieces.push($(this).attr('data-piece'))
});