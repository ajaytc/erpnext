$(".display-file-selector").click(function () {
  $(this).next().trigger("click");
});

$("#proofSubmit").click(function () {
  checkFileUpload("paymentProof").then((res) =>
    frappe.call({
      method: "erpnext.modehero.trimming.submit_payment_proof",
      args: {
        data: {
          order: "{{frappe.form_dict.order}}",
          payment_proof: res,
          comment: $("#proofComment").val(),
        },
      },
      callback: function (r) {
        if (!r.exc) {
          console.log(r);
          frappe.msgprint({
            title: __("Notification"),
            indicator: "green",
            message: __(
              "Trimming Order " +
                "{{trimOrder.name}}'s" +
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
          if ("{{trimOrder.payment_proof}}" == null) {
            console.error("payment proof must upload");
          } else {
            filename = "{{trimOrder.payment_proof}}";
            resolve(filename);
          }
        } else {
          uploadFile(componentId).then((res) => resolve(res));
        }

        break;
      case "confirmation_doc":
        if (!file) {
          if ("{{trimOrder.confirmation_doc}}" == null) {
            console.error("confirmation doc must upload");
          } else {
            filename = "{{trimOrder.confirmation_doc}}";
            resolve(filename);
          }
        } else {
          uploadFile(componentId).then((res) => resolve(res));
        }
        break;
      case "profoma":
        if (!file) {
          if ("{{trimOrder.profoma}}" == null) {
            console.error("profoma must upload");
          } else {
            filename = "{{trimOrder.profoma}}";
            resolve(filename);
          }
        } else {
          uploadFile(componentId).then((res) => resolve(res));
        }

        break;
      case "invoice":
        if (!file) {
          if ("{{trimOrder.invoice}}" == null) {
            console.error("invoice must upload");
          } else {
            filename = "{{trimOrder.invoice}}";
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
    method: "erpnext.modehero.trimming.submit_trim_vendor_summary_info",
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
            "Trimming order " +
              "{{trimOrder.name}}" +
              " summary created successfully"
          ),
        });
      } else {
        frappe.msgprint({
          title: __("Notification"),
          indicator: "red",
          message: __(
            "Trimming order " + "{{trimOrder.name}}" + " summary created Failed"
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
  $("#confirmation_doc-label").html($(this).prop("files")[0].name);
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
