
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
        body = `{{template}}`
        tinymce.get("emailBody").setContent(body);
        subject=`{{subject}}`
        tinymce.get("emailSubject").setContent(subject)

    }, 600);

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
    var tempType = ''
    // console.log(temp)
    var searchParams = new URLSearchParams(window.location.search)

    tempCase = getCase(searchParams)
    tempType = getType(searchParams)


    frappe.call({
        method: 'erpnext.modehero.template.updateTemplate',
        args: {
            data: {
                type: tempType,
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












