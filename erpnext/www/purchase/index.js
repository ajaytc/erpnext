window.onload = function(){
    $('.sum-quantity').each(function(){
        let item = $(this).attr('data-item');
        let size = $(this).attr('data-size');
        let sum = get_sum(item,size);
        $(this).text(sum);
    });
}

$("input[type='checkbox']").change(function(){
    if($(this).attr('data-check_type')=="select-all"){
        return null
    }
    if ($(this).is(':checked')){
        $("."+ $(this).attr('data-order')+"-qnty-content-class").each(function(){
            $(this).attr('contenteditable','true').keypress(function(e) {
                if (isNaN(String.fromCharCode(e.which))) e.preventDefault();
            });
            $(this).addClass("background-ash");
        })
    }
    else{
        $("."+ $(this).attr('data-order')+"-qnty-content-class").each(function(){
            $(this).attr('contenteditable','false');
            $(this).html($(this).attr("data-current_qty"));
            $(this).removeClass("background-ash");
        })
    }
})

function modify(item){
    let order = {}
    $(".sales-order-checkbox-"+item).each(function(){
        let order_name = $(this).attr('data-order');
        $("."+ order_name +"-qnty-content-class").each(function(){
            let size_type = $(this).attr('data-size');
            if ($(this).attr("data-current_qty") ==  $(this).text()){
                
            }
            else{
                if ( order[order_name]==undefined){
                    order[order_name]={}
                }
                order[order_name][size_type]= $(this).text();
            }
        })
    })
    console.log(order)
}

function select_all_chekbox(item) {
    if ($('.select-all-sales-orders-'+item).is(':checked')) {
        $('.sales-order-checkbox-'+item).prop('checked', true).change();
    } else {
        $('.sales-order-checkbox-'+item).prop('checked', false).change();
    }
}

function get_sum(itm_code,size){
    let sum = 0
    $("."+itm_code+"-"+size).each(function() {
        sum = sum + Number($( this ).attr('data-current_qty'));
    });
    return sum
}

function update_sales_order(order){
    console.log(order)
    frappe.call({
        method: 'erpnext.modehero.sales_order.update_sales_order',
        args: {
            order:order
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r.message)
                window.location.reload()
            }
        }
    });
}