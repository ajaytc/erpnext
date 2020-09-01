$(document).ready(function () {
    $('.segment').each(function (index, value) {
        if ($(value).find('.piecesCheck').length == $(value).find('.pieces').length) {
            $(value).find('#fullCheck').show()
        }

    })
});
var both = false

$('.piecesCheck').change(function () {
    plt = false
    invt = false
    checked = $(this).parent().parent().parent().parent().parent().find('input[name="piecesCheck"]:checked');
    $(checked).each(function (index, value) {
        if ($(value).parent().find('.pl').length) {
            plt = true
            $(value).parent().parent().parent().parent().parent().find('#plGen').prop('disabled', true)
            $(value).parent().parent().parent().parent().parent().find('#plNInvGen').prop('disabled', true)
        }
        if ($(value).parent().find('.inv').length) {
            invt = true
            $(value).parent().parent().parent().parent().parent().find('#invGen').prop('disabled', true)
            $(value).parent().parent().parent().parent().parent().find('#plNInvGen').prop('disabled', true)
        }
    })
    if (plt == false) {
        $(this).parent().parent().parent().parent().parent().find('#plGen').prop('disabled', false)
    }
    if (invt == false) {
        $(this).parent().parent().parent().parent().parent().find('#invGen').prop('disabled', false)

    }
    if ((plt == false) && (invt == false)) {
        $(this).parent().parent().parent().parent().parent().find('#plNInvGen').prop('disabled', false)
    }



})

$('.plGen').click(function () {
    generatePL($(this))
})

function generatePL(element) {
    packProductDetails = {}
    el = $(element)
    client = $(el).parent().parent().parent().find('#client').text()
    pos = $(el).parent().parent().parent().find('#pos').attr('data-pos')
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

    if (!jQuery.isEmptyObject(packProductDetails)) {
        frappe.call({
            method: 'erpnext.modehero.uniform.generatePl',
            args: {
                data: {
                    packProductDetails: packProductDetails,
                    client: client,
                    pos: pos
                }
            },
            callback: function (r) {
                if (!r.exc) {
                    console.log(r)
                    if (!both) {
                        $(".piecesCheck").prop("checked", false);
                        location.reload();
                    }


                } else {
                    console.log(r)
                }
            }
        })

    }

}


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
                html = r.message.content
                // html=$.parseHTML(htmlstr)
                html = html.replace('src="brandlogoimage"', "src=" + r.message.brand_logo);
                // $(html).find('#brand_logo').attr("src",r.message.brand_logo)
                // $("#my_image").attr("src","second.jpg");
                render_pdf(html)

            } else {
                console.log(r)
            }
        }
    })

})
$('.inv').click(function () {
    invoiceName = $(this).attr('data-invoice')
    frappe.call({
        method: 'erpnext.modehero.uniform.displayInvDoc',
        args: {
            data: {
                invoice_name: invoiceName
            }
        },
        callback: function (r) {
            if (!r.exc) {
                html = r.message.content
                // html=$.parseHTML(htmlstr)
                html = html.replace('src="brandlogoimage"', "src=" + r.message.brand_logo);
                // $(html).find('#brand_logo').attr("src",r.message.brand_logo)
                // $("#my_image").attr("src","second.jpg");
                render_pdf(html)

            } else {
                console.log(r)
            }
        }
    })

})

var invoiceOnly = ''
var bothInvNPl = ''

$('.invGen').click(function () {
    invoiceOnly = $(this)
    $('#shipmentcost').modal('show')
    
    // generateInvoice($(this))

})

$('#onlyInvoice').click(function () {
    generateInvoice($(invoiceOnly))
})


$('.plNInvGen').click(function () {
    both = true
    bothInvNPl = $(this)
    $('#shipmentcost2').modal('show')
    
})

$('#bothPlNInv').click(function () {
    generatePL($(bothInvNPl))
    generateInvoice($(bothInvNPl))
})
function generateInvoice(element) {
    packProductDetails = {}
    el = $(element)
    client = $(el).parent().parent().parent().find('#client').text()
    if (both) {
        shipmentCost = $('#shipment_cost2').val()
    } else {
        shipmentCost = $('#shipment_cost').val()
    }
    pos = $(el).parent().parent().parent().find('#pos').attr('data-pos')
    fullCheckedEls = $(el).parent().parent().parent().find('input[name="piecesCheck"]:checked')
    $(fullCheckedEls).each(function (index, pack) {
        reciever = $(pack).parent().parent().parent().find('#recieverName').text()
        if (!(reciever in packProductDetails)) {
            packProductDetails[reciever] = []
        }

        packProduct = $(pack).parent().parent()
        product = $(packProduct).find('.product').text()
        item_code = $(packProduct).find('.product').attr('data-item')
        order_no = $(packProduct).find('#order_no').text()
        qty = $(packProduct).find('#qty').text()
        size = $(packProduct).find('#size').text()
        piece_name = $(packProduct).attr('data-piece')
        prodDetail = {}
        prodDetail['product'] = product
        prodDetail['item_code'] = item_code
        prodDetail['size'] = size
        prodDetail['qty'] = qty
        prodDetail['name'] = piece_name

        packProductDetails[reciever].push(prodDetail)

        // packProducts=$(pack).parent().parent().parent().find('.pieces')
        // $(packProducts).each(function (index,packProduct) {


        // })


    })

    if (!jQuery.isEmptyObject(packProductDetails)) {
        frappe.call({
            method: 'erpnext.modehero.uniform.generateInvoice',
            args: {
                data: {
                    packProductDetails: packProductDetails,
                    client: client,
                    pos: pos,
                    shipment_cost: shipmentCost
                }
            },
            callback: function (r) {
                if (!r.exc) {
                    console.log(r)
                    $(".piecesCheck").prop("checked", false);
                    location.reload();

                } else {
                    console.log(r)
                }
            }
        })

    }
}
function render_pdf(html) {
    var formData = new FormData();

    //Push the HTML content into an element
    formData.append("html", html);
    // if (opts.orientation) {
    // 	formData.append("orientation", opts.orientation);
    // }
    var blob = new Blob([], { type: "text/xml" });
    formData.append("blob", blob);

    var xhr = new XMLHttpRequest();
    $("#container").css("opacity", 0.5);
    xhr.open("POST", '/api/method/frappe.utils.print_format.report_to_pdf');
    xhr.setRequestHeader("X-Frappe-CSRF-Token", frappe.csrf_token);
    xhr.responseType = "arraybuffer";

    xhr.onload = function (success) {
        if (this.status === 200) {
            $("#container").css("opacity", 1);
            var blob = new Blob([success.currentTarget.response], { type: "application/pdf" });
            var objectUrl = URL.createObjectURL(blob);
            window.open(objectUrl);
            // target=`<a href="${objectUrl}">${objectUrl}</a>`
            // $('#order_doc').html(target)


            //Open report in a new window
            // window.open(objectUrl);
        }
        else {
            frappe.msgprint({
                title: __("Notification"),
                indicator: "red",
                message: __(
                    "Not Permitted"
                ),
            });
            $(".row").css("opacity", 1);
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