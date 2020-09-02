
window.onload = function(){
    $(".ship-quantity-box").each(function(){
        $(this).keypress(function(e) {
            if (isNaN(String.fromCharCode(e.which)) || e.which == 32) e.preventDefault();
        });
    })
}

$(".add-shipment-info").click(function(){
    let validation_result= validate_tickboxes($(this))
    if (!validation_result[0]){
        return null
    }
    let location = validation_result[1]
    let po_if= validation_result[2]
    let tick_box_element= validation_result[3]
    let sales_order_item = validation_result[4]
    if (tick_box_element.attr("data-ship_data")){
        open_shipment_modal(tick_box_element.attr("data-ship_data"),location,po_if,1)
        return null
    }
    $("#shipment-order-if").empty().append("<option value='"+po_if+"'>"+po_if+"</option>")
    let modal_element = $("#shipment-order-modal")
    modal_element.attr("data-sales_order_item",sales_order_item).attr("data-location",location)
    $("#shipment-order-file").prop("hidden",true)
    if (tick_box_element.hasClass("sent-tick")){
        modal_element.attr("dispatch_name",tick_box_element.attr("data-dispatch"))
    }
    modal_element.modal('show')
})

$("#add-pl-invoice").click()

$(".s-tag-current-shipment").click(function(){ 
    open_shipment_modal($(this).attr("data-ship_data"),$(this).attr("data-location"),$(this).attr("data-poif"))
})

function validate_tickboxes(element){
    let location = $(element).attr("data-location")

    let selected_amt = $("input:checkbox[data-location|='"+location+"']:checked").length
    if (selected_amt==0){
        return [false]
    }
    if (selected_amt>1){
        response_message('Unsuccessfull', 'Multiple selection are not allowed at once to add shipment info!', 'red')
        return [false]
    }    
    let tick_box_element = $("input:checkbox[data-location|='"+location+"']:checked").first()
    let po_if = tick_box_element.attr("data-if")
    let sales_order_item = tick_box_element.attr("data-sales_order_item")
    return [true,location,po_if,tick_box_element,sales_order_item]
}

function open_shipment_modal(data,location,po_if,is_editable){
    data = JSON.parse(data.replace(/'/g, '"'))
    set_modal_data(data,location,po_if)
    $("#shipment-order-modal").modal('show')
}

$("#shipment-order-modal").on("hidden.bs.modal", function () {
    $("#create-shipment-order input").removeAttr("disabled")
    $("#create-shipment-order")[0].reset()
    $("#shipment-order-document-div").removeAttr("hidden")
    $("#shipment-order-save").removeAttr("hidden")
    $("#shipment-order-file").removeAttr("hidden",true).removeAttr("href")
    $(this).removeAttr("data-shipment_name").removeAttr("data-location").removeAttr("data-sales_order_item").removeAttr("data-dispatch_name")
});

function hide_elements(){
    $("#create-shipment-order input").prop("disabled", true)
    $("#shipment-order-document-div").prop("hidden", true)
    $("#shipment-order-save").prop("hidden", true)
}

function set_modal_data(data,location,po_if){
    $("#shipment-order-modal").attr("data-location",location)
    $("#shipment-order-modal").attr("data-shipment_name",data.name)
    $("#shipment-order-if").empty().append("<option value='"+po_if+"'>"+po_if+"</option>")
    $("#shipment-order-ca-company").val(data.carrier_company)
    $("#shipment-order-shipping-price").val(data.shipping_price)
    $("#shipment-order-tracking-number").val(data.tracking_number)
    $("#shipment-order-tracking-link").val(data.html_tracking_link)
    $("#shipment-order-shipping-date").attr( "value",data.shipping_date)
    $("#shipment-order-expected-date").attr( "value",data.expected_delivery_date)
    if (data.shipping_document!=""){
        $("#shipment-order-file").attr("href",data.shipping_document)
    }
    else{
        $("#shipment-order-file").prop("hidden",true)
    }
}

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

function collect_ship_size_qty(){
    let location = $("#shipment-order-modal").attr("data-location")
    let result_obj = {}
    $("input:checkbox[data-location|='"+location+"']:checked").first().parent().parent().children(".ship-quantity-boxs").each(function(){
        result_obj[$(this).children(":input.ship-quantity-box").first().attr("data-size")] = $(this).children(":input.ship-quantity-box").first().val()
    })
    return result_obj
}

function response_message(title, message, color) {
    frappe.msgprint({
        title: __(title),
        indicator: color,
        message: __(message)
    });
}