$(".display-file-selector").click(function () {
  $(this).next().trigger("click");
});

$("#proofSubmit").click(function () {
  checkFileUpload("paymentProof").then((res) =>
    frappe.call({
      method: "erpnext.modehero.package.submit_payment_proof",
      args: {
        data: {
          order: "{{frappe.form_dict.order}}",
          payment_proof: res,
          comment: $("#proofComment").val(),
          confirmation_reminder:$.trim($("#conf_reminder").text()),
          proforma_reminder:$.trim($("#prof_reminder").text()),
          payment_reminder:$.trim($("#paym_reminder").text()),
          shipment_reminder:$.trim($("#shipment_reminder").text()),
          reception_reminder:$.trim($("#recep_reminder").text())
        },
      },
      callback: function (r) {
        if (!r.exc) {
          console.log(r);
          frappe.msgprint({
            title: __("Notification"),
            indicator: "green",
            message: __(
              "Packaging Order " +
                "{{packOrder.name}}'s" +
                " payment proof submitted successfully"
            ),
          });
        }
      },
    })
  );
});

$("#vendorSubmit").click(function () {
  let files = ["confirmation_doc", "profoma", "invoice"];

  Promise.all(
    files.map((f) => {
      return checkFileUpload(f);
    })
  )
    .then((files) => {
      console.log(files);
      submitVendorSummary(files);
    })
    .catch((e) => {
      frappe.throw(e);
    });
});

function checkFileUpload(componentId) {
  return new Promise((resolve, reject) => {
    let file = $(`#${componentId}`).prop("files")[0];
    switch (componentId) {
      case "paymentProof":
        if (!file) {
          if ("{{packOrder.payment_proof}}" == null) {
            console.error("payment proof must upload");
          } else {
            filename = "{{packOrder.payment_proof}}";
            resolve(filename);
          }
        } else {
          uploadFile(componentId).then((res) => resolve(res));
        }

        break;
      case "confirmation_doc":
        if (!file) {
          if ("{{packOrder.confirmation_doc}}" == null) {
            console.error("confirmation doc must upload");
          } else {
            filename = "{{packOrder.confirmation_doc}}";
            resolve(filename);
          }
        } else {
          uploadFile(componentId).then((res) => resolve(res));
        }
        break;
      case "profoma":
        if (!file) {
          if ("{{packOrder.profoma}}" == null) {
            console.error("profoma must upload");
          } else {
            filename = "{{packOrder.profoma}}";
            resolve(filename);
          }
        } else {
          uploadFile(componentId).then((res) => resolve(res));
        }

        break;
      case "invoice":
        if (!file) {
          if ("{{packOrder.invoice}}" == null) {
            console.error("invoice must upload");
          } else {
            filename = "{{packOrder.invoice}}";
            resolve(filename);
          }
        } else {
          uploadFile(componentId).then((res) => resolve(res));
        }

        break;
    }
  });
}

function submitVendorSummary(files) {
  frappe.call({
    method: "erpnext.modehero.package.submit_pack_vendor_summary_info",
    args: {
      data: {
        order: "{{frappe.form_dict.order}}",
        ex_work_date: $("#exWorkDate").val(),
        confirmation_doc: files[0],
        profoma: files[1],
        invoice: files[2],
        carrier: $("#carrier").val(),
        tracking_number: $("#tracking_number").val(),
        shipment_date: $("#shipmentDate").val(),
        expected_date: $("#expectedDate").val(),
        shipping_price: $("#shipping_price").val(),
        html_tracking_link: $("#html_tracking_link").val(),
        production_comment: $("#comment").val(),
      },
    },
    callback: function (r) {
      if (!r.exc) {
        console.log(r);
        frappe.msgprint({
          title: __("Notification"),
          indicator: "green",
          message: __(
            "Packaging order " +
              "{{packOrder.name}}" +
              " summary created successfully"
          ),
        });
      } else {
        frappe.msgprint({
          title: __("Notification"),
          indicator: "red",
          message: __(
            "Packaging order " +
              "{{packOrder.name}}" +
              " summary created Failed"
          ),
        });
      }
    },
  });
}

function uploadFile(componentId) {
  return new Promise((resolve, reject) => {
    let file = $(`#${componentId}`).prop("files")[0];
    if (file.size / 1024 / 1024 > 5) {
      reject("Please upload file less than 5mb");
    }
    var reader = new FileReader();
    reader.readAsDataURL(file);
    console.log(file, reader, reader.result);
    reader.onload = function () {
      frappe.call({
        method: "frappe.handler.uploadfile",
        // method: 'erpnext.modehero.sales_order.upload_test',
        args: {
          filename: file.name,
          attached_to_doctype: "Production Order",
          attached_to_field: componentId,
          is_private: true,
          filedata: reader.result,
          from_form: true,
        },
        callback: function (r) {
          if (!r.exc) {
            console.log(r);
            $(`#${componentId}-label`).html(r.message.file_url);
            resolve(r.message.file_url);
          }
        },
      });
    };
  });
}

$("#paymentProof").change(function () {
  $("#paymentProof-label").html($(this).prop("files")[0].name);
});

$("#confirmation_doc").change(function () {
  $("#confirmation_doc-label").html($(this).prop("files")[0].name);
});

$("#profoma").change(function () {
  $("#profoma-label").html($(this).prop("files")[0].name);
});

$("#invoice").change(function () {
  $("#invoice-label").html($(this).prop("files")[0].name);
});
