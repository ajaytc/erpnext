var SUPPLY_TABLE = '<div class="table-wrapper table-responsive mt-2">\
                        <table class="table table-sm table-striped">\
                            <thead>\
                                <th></th>\
                                <th>Destination</th>\
                                <th>Product</th>\
                                <th>Number of pieces</th>\
                                <th>Consumption per piece</th>\
                                <th>Total consumption</th>\
                                <th>Safety margin</th>\
                                <th>Theoritical order</th>\
                                <th>Minimum order quantity</th>\
                                <th>ORDER</th>\
                                <th>Stock at destination</th>\
                                <th>Internal referance</th>\
                                <th></th>\
                            </thead>\
                            <tbody class="tbody-supply-order-section">\
                            </tbody>\
                        </table>\
                    </div>'


window.onload = function(){
    $(".client-modal-link").css("color","#3B3DBF");
    $('.sum-quantity').each(function(){
        let item = $(this).attr('data-item');
        let size = $(this).attr('data-size');
        let sum = get_sum(item,size);
        $(this).text(sum);
    });
    $('.total-sum').each(function(){
        let item = $(this).attr('data-item');
        let total_sum = get_total_sum(item);
        $(this).text("Total : "+total_sum.toString());
    });
    $(".default-hide").hide().find('input').prop('disabled', true)
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

function set_modify(item){
    $('.modify-show-'+item).show().find('input').prop('disabled', false)
    $('.modify-hide-'+item).hide().find('input').prop('disabled', true)
}

function cancel_modify(item){
    $('input:checkbox').prop('checked', false).change();
    $('.modify-show-'+item).hide().find('input').prop('disabled', true)
    $('.modify-hide-'+item).show().find('input').prop('disabled', false)
}

function modify(item){
    let order = collect_data_for_modify(item);
    cancel_modify(item)
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
    let order = collect_data_for_validate(item);
    if (order==null){
        response_message('Unsuccessfull', 'Incomplete data !', 'red')
        return null
    }
    else if(order=="select_all_error"){
        response_message('Unsuccessfull', 'All orders of the block should be selected before validation !', 'red')
        return null
    }
    else if(order=="factory_error"){
        response_message('Unsuccessfull', 'Factory is not selected !', 'red')
        return null
    }
    console.log(order)
    set_supply_order_section(item,order)
    // frappe.call({
    //     method: 'erpnext.modehero.sales_order.validate_sales_item_orders',
    //     args: {
    //         orders_object:order.order
    //     },
    //     callback: function (r) {
    //         if (r) {
    //             if (r.message['status'] == "ok") {
    //                 response_message('Successfull', 'Orders validated successfully', 'green')
    //                 window.location.reload()
    //                 return null;
    //             }
    //             response_message('Unsuccessfull', 'Orders validated unsuccessfully', 'red')
    //             window.location.reload()
    //             return null
    //         }
    //         response_message('Unsuccessfull', 'Orders validated unsuccessfully', 'red')
    //     }
    // });
}

function cancel(item){
    let orders = []
    $("tr[data-item_code|='"+item+"']").each(function(){
        let order_name = $(this).attr('data-order');
        orders.push(order_name);
    })

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

function collect_data_for_validate(item){
    let order = {}
    let is_any_empty = false;
    if (!$(".factory-select[data-item_code|='"+item+"']").val()){
        return "factory_error"
    }

    $("tr[data-item_code|='"+item+"']").each(function(){
        let order_name = $(this).attr('data-order');
        let order_count = $(this).attr('data-order_count');

        order[order_name]={"client_name":$(this).attr("data-client_name"),"sizes":{}}

        $("."+ order_count +"-qnty-content-class").each(function(){
            let size_type = $(this).attr('data-size');
            if ($(this).text().trim().length==0){
                is_any_empty = true;
                return false;
            }
            if (!(isNaN($(this).text()))){
                if ( order[order_name]==undefined){
                    order[order_name]={}
                    order[order_name]["sizes"]={}
                }
                order[order_name]["sizes"][size_type]= parseInt($(this).text());
            }
        })     
    })
    let factory = $(".factory-select[data-item_code|='"+item+"']").val()
    let full_data = {"factory_name":$("option[value|='"+factory+"']").attr("data-factory_name") ,"factory":factory,"order":order}
    $('input:checkbox').prop('checked', false).change();
    if (is_any_empty){
        return null
    }
    if(Object.keys(full_data.order).length==0){
        return null
    }
    return full_data
}


function collect_data_for_modify(item){
    let is_any_checked = false;
    let is_any_empty = false;
    $(".sales-order-checkbox[data-item_code|='"+item+"']").each(function(){
        if ($(this).is(':checked')){
            is_any_checked = true;
        }
    });
    if (!is_any_checked){
        return null;
    }
    let order = {}
    $(".sales-order-checkbox[data-item_code|='"+item+"']").each(function(){
        if ($(this).is(':checked')){
            let order_name = $(this).attr('data-order');
            let order_count = $(this).attr('data-order_count');

            $("."+ order_count +"-qnty-content-class").each(function(){
                let size_type = $(this).attr('data-size');
                if ($(this).text().trim().length==0){
                    is_any_empty = true;
                    return false;
                }
                if (!(isNaN($(this).text()))&&($(this).attr("data-current_qty") !=  $(this).text())){
                    if ( order[order_name]==undefined){
                        order[order_name]={}
                        order[order_name]["sizes"]={}
                    }
                    order[order_name]["sizes"][size_type]= parseInt($(this).text());
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

async function set_supply_order_section(item,order){
    let item_details = null
    await frappe.call({
        method: 'erpnext.modehero.product.get_product_item',
        args: {
            product:item
        },
        callback: function (r) {
            if (!r.exc) {
                item_details= r.message
                return null
            }
            response_message('Unsuccessfull', 'Error !', 'red')
            return null
        }
    });

    if (item_details!=null){
        change_supplier_division(item_details,order)
    }
}

function change_supplier_division(item,order){
    item.supplier = [{"name":123,"supplier_name":"test1"}]
    let supplieres = item.supplier
    for (let i=0;i<supplieres.length;i++){
        if ($(".suppliere-block[data-supplier|='"+supplieres[i]+"']").length==0){
            let markup = '<div class="suppliere-block" data-supplier="'+supplieres[i].name+'" >\
                            <h3>'+supplieres[i].supplier_name+'</h3>\
                          </div>'
            $("#supply-order-section").append(markup)
            $(".suppliere-block[data-supplier|='"+supplieres[i].name+"']").append(SUPPLY_TABLE)
        }
        let tbody_element = $(".suppliere-block[data-supplier|='"+supplieres[i].name+"'] > .table-wrapper > table > .tbody-supply-order-section")
        add_supply_block_table_body(tbody_element,supplieres[i],item,order)
    }
}

function add_supply_block_table_body(tbody_element,supplier,item,order){
    let total_order_details = get_total_order_detail(order)
    let markup = '\
    <tr data-suppliere_row_item="'+item.name+'" >\
        <td class="select-box-supply-product"></td>\
        <td class="destination-supply-product">'+order.factory_name+'</td>\
        <td class="product-supply-product">'+item.item_name+'</td>\
        <td class="nop-supply-product"></td>\
        <td class="cpp-supply-product"></td>\
        <td class="sm-supply-product"></td>\
        <td class="to-supply-product"></td>\
        <td class="moq-supply-product"></td>\
        <td class="order-supply-prodcut"></td>\
        <td class="sat-supply-product"></td>\
        <td class="if-supply-product"></td>\
        <td class="reminder-supply-product"></td>\
    </tr>'
    tbody_element.append(markup)
}

function get_total_order_detail(order){
    let total_prod = 0
    for (const sales_order_item in order.order){
        
    }
}

function select_all_chekbox(item) {
    if ($(".select-all-sales-orders[data-item_code|='"+item+"']").is(':checked')) {
        $(".sales-order-checkbox[data-item_code|='"+item+"']").prop('checked', true).change();
    } else {
        $(".sales-order-checkbox[data-item_code|='"+item+"']").prop('checked', false).change();
    }
}

function get_total_sum(itm_code){
    let sum = 0;
    $(".sum-quantity[data-item|='"+itm_code+"']").each(function() {
        sum = sum + Number($( this ).text());
    });
    return sum
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