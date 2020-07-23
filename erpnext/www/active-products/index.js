$("#modify-button").click(function(){
    if($(".selected-active-product:checked").length!=1){
        response_message('Unsuccessfull', 'Please tick one checkbox', 'red');
        return null;
    }
    location.href = "/product-attribution_pricing?attribution_pricing="+$(".selected-active-product:checked").attr("data-active-product");
})

$("#deactivate-button").click(function(){
    if($(".selected-active-product:checked").length==0){
        return null;
    }
    let name_list = []
    $(".selected-active-product").each(function(){
        if ($(this).is(':checked')){
            name_list.push($(this).attr("data-active-product"));
        }
    })
    frappe.call({
        method: 'erpnext.modehero.customer.deactivate_pricing',
        args: {
            name_list : name_list
        },
        callback: function (r) {
            if (r) {
                if (r.message['status'] == "ok") {
                    response_message('Successfull', 'Pricing Attribution deactivated successfully', 'green');
                    location.href = "/active-products";
                    return null;
                }
                response_message('Unsuccessfull', 'Pricing Attribution deactivated unsuccessfully', 'red');
                location.href = "/active-products";                
                return null;
            }
            response_message('Unsuccessfull', 'Pricing Attribution deactivated unsuccessfully', 'red');
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