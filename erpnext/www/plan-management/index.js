$('#submit').click(function () {
    data={}
    planNames=[]
    $('.planName').each(function () {
        planName=$(this).val()
        name=$(this).attr('data-plan_name')
        planNames.push(planName)
        data[planName]={} 
        data[planName]['name']=name
    })
    $('.accessPart').each(function(){
        accessPart=$(this).text()
        if($(this).parent().find("input[type=checkbox]").length>0){
            $(this).parent().find("input[type=checkbox]").each(function(idx){
                plan=$('.planName')[idx].value
                checked=$(this).is(':checked')
                data[plan][accessPart]=checked
            })
        }else if($(this).parent().find("input[type=text]").length>0){
            $(this).parent().find("input[type=text]").each(function(idx){
                plan=$('.planName')[idx].value
                value=$(this).val()
                data[plan][accessPart]=value
            })
        }
        
    })
    trial_period=$('#trial_period').val()

    frappe.call({
        method: 'erpnext.modehero.payment_plan.savePaymentPlan',
        args: {
            data: data,
            trial_period:trial_period
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
                frappe.msgprint({
                    title: __("Notification"),
                    indicator: "green",
                    message: __(
                      "Payment plans saved successfully"
                    ),
                  });


            } else {
                console.log(r)
                frappe.msgprint({
                    title: __("Notification"),
                    indicator: "red",
                    message: __(
                      "Payment plans save failed"
                    ),
                  });
            }
        }
    })
})