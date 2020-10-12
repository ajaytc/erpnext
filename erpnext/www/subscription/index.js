

$('.annualPay').click(function () {
  plan_name=$(this).attr('data-name')
  window.location.href = "/payment?name="+plan_name+"&period=Annually";
    
})

$('.monthPay').click(function () {
  plan_name=$(this).attr('data-name')
  window.location.href = "/payment?name="+plan_name+"&period=Monthly";
    
})

$('#pdf_doc').click(function () {

  let page = $('#doc').html()
  render_pdf(page)
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
  $(".row").css("opacity", 0.5);
  xhr.open("POST", '/api/method/frappe.utils.print_format.report_to_pdf');
  xhr.setRequestHeader("X-Frappe-CSRF-Token", frappe.csrf_token);
  xhr.responseType = "arraybuffer";

  xhr.onload = function (success) {
    if (this.status === 200) {
      $(".row").css("opacity", 1);
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