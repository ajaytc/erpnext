window.onload = function(){
    $(".client-modal-link").css("color","#3B3DBF");
    $('.sum-quantity').each(function(){
        let item = $(this).attr('data-item');
        let size = $(this).attr('data-size');
        let sum = get_sum(item,size);
        $(this).text(sum);
    });
}

$(".client-modal-link").click(function(){
    let data_array = ["country","city","phone","email","cusname"];
    for (let k=0;k<data_array.length;k++){
        $("#modal-"+data_array[k]).text($(this).attr("data-"+data_array[k]));
    }
    $("#client-modal").modal('show');
});

$("input[type='checkbox']").change(function(){
    if($(this).attr('data-check_type')=="select-all"){
        return null
    }
    if ($(this).is(':checked')){
        $("."+ $(this).attr('data-order_count')+"-qnty-content-class").each(function(){
            $(this).attr('contenteditable','true').keypress(function(e) {
                if (isNaN(String.fromCharCode(e.which)) || e.which == 32) e.preventDefault();
            });
            $(this).addClass("background-ash");
        })
    }
    else{
        $("."+ $(this).attr('data-order_count')+"-qnty-content-class").each(function(){
            $(this).attr('contenteditable','false');
            $(this).html($(this).attr("data-current_qty"));
            $(this).removeClass("background-ash");
        })
    }
})

function modify(item){
    let order = collect_data(item,false);
    if (order==null){
        response_message('Unsuccessfull', 'Incomplete data !', 'red')
        return null
    }
    frappe.call({
        method: 'erpnext.modehero.sales_order.modify_sales_item_orders',
        args: {
            orders_object:order
        },
        callback: function (r) {
            if (r) {
                if (r.message['status'] == "ok") {
                    response_message('Successfull', 'Orders updated successfully', 'green')
                    window.location.reload()
                    return null;
                }
                response_message('Unsuccessfull', 'Orders updated unsuccessfully', 'red')
                window.location.reload()
                return null
            }
            response_message('Unsuccessfull', 'Orders updated unsuccessfully', 'red')
        }
    });
}

function validate(item){
    let order = collect_data(item,true);
    if (order==null){
        response_message('Unsuccessfull', 'Incomplete data !', 'red')
        return null
    }
    frappe.call({
        method: 'erpnext.modehero.sales_order.validate_sales_item_orders',
        args: {
            orders_object:order
        },
        callback: function (r) {
            if (r) {
                if (r.message['status'] == "ok") {
                    response_message('Successfull', 'Orders validated successfully', 'green')
                    window.location.reload()
                    return null;
                }
                response_message('Unsuccessfull', 'Orders validated unsuccessfully', 'red')
                window.location.reload()
                return null
            }
            response_message('Unsuccessfull', 'Orders validated unsuccessfully', 'red')
        }
    });
}

function cancel(item){
    let is_any_checked = false;
    $(".sales-order-checkbox[data-item_code|='"+item+"']").each(function(){
        if ($(this).is(':checked')){
            is_any_checked = true;
        }
    })
    if (!is_any_checked){
        return null
    }
    let orders = []
    $(".sales-order-checkbox[data-item_code|='"+item+"']").each(function(){
        if ($(this).is(':checked')){
            let order_name = $(this).attr('data-order');
            orders.push(order_name);
        }
    })
    if (orders.length==0){
        return null
    }
    $('input:checkbox').prop('checked', false);
    frappe.call({
        method: 'erpnext.modehero.sales_order.cancel_sales_item_orders',
        args: {
            item_order_list:orders
        },
        callback: function (r) {
            if (r) {
                if (r.message['status'] == "ok") {
                    response_message('Successfull', 'Orders canceled successfully', 'green')
                    window.location.reload()
                    return null;
                }
                response_message('Unsuccessfull', 'Orders canceled unsuccessfully', 'red')
                window.location.reload()
                return null
            }
            response_message('Unsuccessfull', 'Orders canceled unsuccessfully', 'red')
        }
    });
}

function collect_data(item,for_validations){
    let is_any_checked = false;
    let is_any_empty = false;
    $(".sales-order-checkbox[data-item_code|='"+item+"']").each(function(){
        if ($(this).is(':checked')){
            is_any_checked = true;
        }
    });
    if (!is_any_checked){
        return null
    }
    let order = {}
    $(".sales-order-checkbox[data-item_code|='"+item+"']").each(function(){
        if ($(this).is(':checked')){
            let order_name = $(this).attr('data-order');
            let order_count = $(this).attr('data-order_count');

            if (for_validations){
                order[order_name]={}
            }
            $("."+ order_count +"-qnty-content-class").each(function(){
                let size_type = $(this).attr('data-size');
                if ($(this).text().trim().length==0){
                    is_any_empty = true;
                    return false;
                }
                if (!(isNaN($(this).text()))&&($(this).attr("data-current_qty") !=  $(this).text())){
                    if ( order[order_name]==undefined){
                        order[order_name]={}
                    }
                    order[order_name][size_type]= parseInt($(this).text());
                }
            })
        }        
    })
    $('input:checkbox').prop('checked', false).change();
    if (is_any_empty){
        return null
    }
    if(Object.keys(order).length==0){
        return null
    }
    return order
}

function select_all_chekbox(item) {
    if ($(".select-all-sales-orders[data-item_code|='"+item+"']").is(':checked')) {
        $(".sales-order-checkbox[data-item_code|='"+item+"']").prop('checked', true).change();
    } else {
        $(".sales-order-checkbox[data-item_code|='"+item+"']").prop('checked', false).change();
    }
}

function get_sum(itm_code,size){
    let sum = 0
    $(".qnty-content-class[data-item_code|='"+itm_code+"'][data-size|='"+size+"']").each(function() {
        sum = sum + Number($( this ).attr('data-current_qty'));
    });
    return sum
}

function response_message(title, message, color) {
    frappe.msgprint({
        title: __(title),
        indicator: color,
        message: __(message)
    });
}