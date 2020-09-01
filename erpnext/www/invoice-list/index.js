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