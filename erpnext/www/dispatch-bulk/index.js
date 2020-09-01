

window.onload = function(){
    $(".ship-quantity-box").each(function(){
        $(this).keypress(function(e) {
            if (isNaN(String.fromCharCode(e.which)) || e.which == 32) e.preventDefault();
        });
    })
}

$(".add-shipment-info").click(function(){
    let location = $(this).attr("data-location")
    
    let selected_amt = $("input:checkbox[data-location|='"+location+"']:checked").length
    if (selected_amt==0){
        return null
    }
    if (selected_amt>1){
        response_message('Unsuccessfull', 'Multiple selection are not allowed at once !', 'red')
        return null
    }
    if (!validate_ship_quantity($("input:checkbox[data-location|='"+location+"']:checked").first())){
        response_message('Unsuccessfull', 'Fill all quantities!', 'red')
        return null
    }
    
    let po_if = $("input:checkbox[data-location|='"+location+"']:checked").first().attr("data-if")
    let sales_order_item = $("input:checkbox[data-location|='"+location+"']:checked").first().attr("data-sales_order_item")
    $("#shipment-order-if").empty().append("<option value='"+po_if+"'>"+po_if+"</option>")
    $("#shipment-order-modal").attr("data-location",location)
    $("#shipment-order-modal").attr("data-sales_order_item",sales_order_item)
    $("#shipment-order-modal").modal('show')
})

function validate_ship_quantity(tick_box_element){
    let validated = true
    tick_box_element.parent().parent().children(".ship-quantity-boxs").each(function(){
        if ($(this).children(":input.ship-quantity-box").first().val().trim().length==0){
            validated = false
            return false
        }
    })
    return validated
}

function response_message(title, message, color) {
    frappe.msgprint({
        title: __(title),
        indicator: color,
        message: __(message)
    });
}