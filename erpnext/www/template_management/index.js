
$(document).ready(function () {


    setTimeout(() => {
        // t=$('#order_document').html();
        // tinymce.get("editor").setContent(t);
        // console.log(t)
        {% if case== 'pdf' %}
        $('#subjectBlock').hide()
        $('#bodyTag').hide()
        {% endif %}
        
        initTiny()
        
       

    }, 200);

    setTimeout(() => {
        $('.tox-notifications-container').hide()
    }, 3000);


})

$('#pdfTempNames').change(function () {
    let tempName = $(this).find('option:selected').val()

    frappe.call({
        method: 'erpnext.modehero.template.getPdfTemplate',
        args: {
            data: {
                name: tempName
            }
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
                tinymce.get("emailBody").setContent('rwerwerwrwewwrwqwrqwrqwrwe');
                tinymce.get("emailBody").setContent(r.message.template.content);


            } else {
                frappe.msgprint({
                    title: __('Notification'),
                    indicator: 'red',
                    message: __('Template Retrieval Failed')
                });
            }
        }
    })

})

$('#emailTempNames').change(function () {
    let tempName = $(this).find('option:selected').val()

    frappe.call({
        method: 'erpnext.modehero.template.getEmailTemplate',
        args: {
            data: {
                name: tempName
            }
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
                tinymce.get("emailBody").setContent(r.message.template.message);
                tinymce.get("emailSubject").setContent(r.message.template.subject);

            } else {
                frappe.msgprint({
                    title: __('Notification'),
                    indicator: 'red',
                    message: __('Template Retrieval Failed')
                });
            }
        }
    })

})

function initTiny(params) {


    tinymce.init({
        selector: '.edit',
        plugins: 'a11ychecker advcode casechange formatpainter linkchecker autolink lists checklist media mediaembed pageembed permanentpen powerpaste table advtable tinycomments tinymcespellchecker',
        toolbar: 'a11ycheck addcomment showcomments casechange checklist code formatpainter pageembed permanentpen table',
        toolbar_mode: 'floating',
        tinycomments_mode: 'embedded',
        tinycomments_author: 'Author name',
    });




}


$('#get').click(function () {

})

$('#submit').click(function () {
    var deltaSubject = tinymce.get("emailSubject").getContent()
    var deltaBody=tinymce.get("emailBody").getContent()
    deltaSubject=deltaSubject.replaceAll('<p>','');
    deltaSubject=deltaSubject.replaceAll('</p>','');
    deltaSubject=deltaSubject.replaceAll('&nbsp;','');
    var tempCase = ''
    var tempName = ''
    // console.log(temp)
    var searchParams = new URLSearchParams(window.location.search)

    tempCase = getCase(searchParams)
    // tempType = getType(searchParams)

    if(tempCase=='pdf'){
        tempName=$('#pdfTempNames').find('option:selected').val()
    }else if(tempCase=='email'){
        tempName=$('#emailTempNames').find('option:selected').val()
    }

    frappe.call({
        method: 'erpnext.modehero.template.updateTemplate',
        args: {
            data: {
                name: tempName,
                case: tempCase,
                template: deltaBody,
                subject:deltaSubject

            }
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
                frappe.msgprint({
                    title: __('Notification'),
                    indicator: 'green',
                    message: __('Template Saved Successfully')
                });


            } else {
                frappe.msgprint({
                    title: __('Notification'),
                    indicator: 'red',
                    message: __('Template Saving Failed')
                });
            }
        }
    })
})

function getCase(searchParams) {
    if (searchParams.has('case')) {
        tempCase = searchParams.get('case')
        return tempCase
    } else {
        frappe.msgprint({
            title: __('Notification'),
            indicator: 'red',
            message: __('Invalid Request')
        });
        return 0;
    }

}

function getType(searchParams) {
    if (searchParams.has('type')) {
        tempType = searchParams.get('type')
        return tempType
    } else {
        frappe.msgprint({
            title: __('Notification'),
            indicator: 'red',
            message: __('Invalid Request')
        });
        return 0;
    }
}












