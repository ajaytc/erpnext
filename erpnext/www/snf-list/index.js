$("#mo-button").click(function(){
    let official_data = []
    $(".selected-snf").each(function(){
        if ($(this).is(':checked')){
            official_data.push(
                {
                    "name":$(this).attr("data-snf-name"),
                    "type":$(this).attr("data-snf-type")
                }
            )
        }
    })
    if (official_data.length==0){
        return null
    }
    frappe.call({
        method: 'erpnext.modehero.bo.make_official',
        args:{
            official_wanted:official_data
        },
        callback: function (r) {
            if (r) {
                if (r.message['status'] == "ok") {
                    response_message('Successfull', 'S&F set official successfull!', 'red')
                    window.location.reload()
                    return null
                }
                response_message('Unsuccessfull', 'S&F set official unsuccessfull!', 'red')
                window.location.reload()
                return null;
            }
            response_message('Unsuccessfull', 'S&F set official  unsuccessfull!', 'red')
        }
    });
})

$("#as-button").click(function(){
    let count = 0
    let snf_type = ""
    let snf_name = ""
    $(".selected-snf").each(function(){
        if ($(this).is(':checked')){
            count = count + 1
            snf_name=$(this).attr("data-snf-name"),
            snf_type =$(this).attr("data-snf-type")
        }
    })
    if (count!=1){
        response_message('Unsuccessfull', 'Please select a checkbox!', 'red')
        return null
    }
    $("#subscription-modal").attr("data-snf_name",snf_name)
    $("#subscription-modal").attr("data-snf_type",snf_type)
    $("#subscription-modal").modal('show');
});

$("#shipment-order-save").click(function(){
    let dates = {}
    dates["start_date"] = $("#subscription-start-date").val()
    dates["end_date"] = $("#subscription-end-date").val()
    if (dates["start_date"]=="" || dates["end_date"]==""){
        response_message('Unsuccessfull', 'Please select both dates!', 'red')
        return null
    }
    if (new Date(dates["start_date"]).getTime()>new Date(dates["end_date"]).getTime()){
        response_message('Unsuccessfull', 'Please select dates correctly!', 'red')
        return null
    }
    frappe.call({
        method: 'erpnext.modehero.bo.add_subscription_to_snf',
        args:{
            dates:dates,
            snf_type:$("#subscription-modal").attr("data-snf_type"),
            snf_name:$("#subscription-modal").attr("data-snf_name")
        },
        callback: function (r) {
            if (r) {
                if (r.message['status'] == "ok") {
                    response_message('Successfull', 'S&F set official successfull!', 'red')
                    window.location.reload()
                    return null
                }
                response_message('Unsuccessfull', 'S&F set official unsuccessfull!', 'red')
                window.location.reload()
                return null;
            }
            response_message('Unsuccessfull', 'S&F set official  unsuccessfull!', 'red')
        }
    });
})

function response_message(title, message, color) {
    frappe.msgprint({
        title: __(title),
        indicator: color,
        message: __(message)
    });
}


