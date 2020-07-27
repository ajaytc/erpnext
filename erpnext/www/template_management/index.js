
$(document).ready(function(){


    setTimeout(() => {
        t=$('#order_document').html();
        tinymce.get("editor").setContent(t);
        console.log(t)

    }, 200);
    
    
})


$('#get').click(function () {
    t=`{{template}}`
    tinymce.get("editor").setContent(t);
})

$('#submit').click(function () {
    var delta = tinymce.get("editor").getContent();
    // console.log(temp)

    frappe.call({
        method: 'erpnext.modehero.template.updateTemplate',
        args: {
            data: {
                type: 'Bulk Order',
                template: delta
            }
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
                frappe.msgprint({
                    title: __('Notification'),
                    indicator: 'green',
                    message: __('Bulk Order Template Saved Successfully')
                });


            } else {
                frappe.msgprint({
                    title: __('Notification'),
                    indicator: 'red',
                    message: __('Bulk Order Template Saving Failed')
                });
            }
        }
    })
})













