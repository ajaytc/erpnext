window.onload= (event)=>{
    let numeric_list = [$(".modifiable-row"),$(".table-input-1.from"),$(".table-input-1.to")]
    for (i=0;i<numeric_list.length;i++){
        numeric_only_event(numeric_list[i])
    }
    float_values_allowance_for_input($(".default-option-price"))
    float_values_allowance_for_div($(".table-input-1.price"))
}

$("#product-category-select").change(function(){
    set_products_at_select_change();
})
$("#client-name-select").change(function(){
    set_products_at_select_change();
})

$("#select-all-check").change(function(){
    if ($(this).is(':checked')) {
        $(".checkbox-table-row").prop('checked', true).change();
    } else {
        $(".checkbox-table-row").prop('checked', false).change();
    }
});



$("#minimum-order").keypress(function(e) {
    if (isNaN(String.fromCharCode(e.which))) e.preventDefault();
})

$("#modify").click(function(){
    let form_data = collect_all_data();
    if (form_data==null){
        return null
    }
    let active_product_name = $(this).attr("ap-name")
    frappe.call({
        method: 'erpnext.modehero.customer.modify_pricing',
        args: {
            form_data:form_data,
            name : active_product_name
        },
        callback: function (r) {
            if (r.hasOwnProperty("message") && !r.exc) {
                if (r.message['status'] == "ok") {
                    response_message('Successfull', 'Pricing Attribution updated successfully', 'green');
                    window.location.href = "/active-products";
                    return null;
                }
                response_message('Unsuccessfull', 'Pricing Attribution updated unsuccessfully', 'red');
                window.location.href = "/active-products";                
                return null;
            }
            response_message('Unsuccessfull', 'Pricing Attribution updated unsuccessfully', 'red');
        }
    });
})

$("#submit").click(function(){
    let form_data = collect_all_data();
    if (form_data==null){
        return null
    }
    frappe.call({
        method: 'erpnext.modehero.customer.set_pricing',
        args: {
            form_data:form_data
        },
        callback: function (r) {
            if (r.hasOwnProperty("message") && !r.exc) {
                if (r.message['status'] == "ok") {
                    response_message('Successfull', 'Pricing Attribution created successfully', 'green')
                    window.location.reload(true)
                    return null;
                }
                response_message('Unsuccessfull', 'Pricing Attribution created unsuccessfully', 'red')
                window.location.reload(true)
                return null
            }
            response_message('Unsuccessfull', 'Pricing Attribution created unsuccessfully', 'red')
        }
    });
})

function set_products_at_select_change(){
    let category =  $('#product-category-select option:selected').val();
    let client = $('#client-name-select option:selected').val();
    if (!category){
        return null
    }
    if (!client){
        return null
    }
    $("#product-select").find("option").remove();
    let prices_items = get_priced_items(client,category);
    if (prices_items==null){
        set_disable_option()
        return null
    }
    frappe.call({
        method: 'erpnext.modehero.product.get_priducts_of_category',
        args: {
            category:category
        },
        callback: function (r) {
            if (!r.message) {
                set_disable_option()
                return null
            }
            let objects=r.message
            let is_empty = true
            if (objects.length>0){
                for (i = 0; i < objects.length; i++) {
                    if (!(prices_items.includes(objects[i].name))){
                        let temp_markup = '<option  value="'+objects[i].name+'">'+objects[i].item_name+'</option>';
                        $("#product-select").append(temp_markup);
                        is_empty = false
                    }
                }
                if (is_empty){
                    set_disable_option()
                }
            }
            else{
                set_disable_option()
            }
        }
    });
}

function get_priced_items(client,category){
    let priced_list = []
    frappe.call({
        method: 'erpnext.modehero.product.get_priced_products',
        args: {
            client:client,
            category:category
        },
        callback: function (r) {
            if (!r.message) {
                return null
            }
            let objects=r.message
            if (objects.length>0){
                for (i = 0; i < objects.length; i++) {
                    priced_list.push(objects[i].item_code);                    
                }
            }
            else{
                return []
            }
        }
    });
    return priced_list
}

function set_disable_option(){
    let temp_markup = '<option  value="" disabled selected>No Product Available</option>';
    $("#product-select").append(temp_markup);
}

function collect_all_data(){
    let select_inputs = collect_select_inputs();
    if (select_inputs=="false"){
        return null;
    }
    let options = collect_options();
    if (options=="false"){
        return null;
    }
    let wholesale_prices = collect_wholesale_prices();
    if (wholesale_prices=="false"){
        return null;
    }
    let season_input = $("#season-input").val();
    if (season_input.trim().length==0){
        response_message('Unsuccessfull', 'Inputs Incompleted!', 'red');
        return null;
    }
    let minimum_order = $("#minimum-order").val();
    if (minimum_order.trim().length==0){
        minimum_order = 0;
    }
    minimum_order = parseInt(minimum_order);
    let show_price = false;
    if ($("#show-price").is(':checked')) {
        show_price = true;
    }
    return {
        'pricing_options':options,
        'wholesale_price':wholesale_prices,
        'show_price':show_price,
        'minimum_order':minimum_order,
        'season':season_input,
        'item_code':select_inputs.product_name,
        'item_group':select_inputs.product_category,
        'client':select_inputs.client_name
    }
}

function collect_options(){
    let option_objs = [];
    let is_any_partial_empty = false;
    $(".option-inputs").each(function(){
        let option = $(this).children(".option-block").children(".option-option").val();
        let price = $(this).children(".price-block").children(".option-price").val();

        if (option.trim().length!=0 && price.trim().length==0){
            is_any_partial_empty = true;
            return false;
        }
        else if(option.trim().length==0 && price.trim().length!=0){
            is_any_partial_empty = true;
            return false;
        }
        else if (option.trim().length==0 && price.trim().length==0){
            return true;
        }
        else{
            option_objs.push({
                'option':option,
                'price':price
            });
        }
    })
    if (is_any_partial_empty){
        response_message('Unsuccessfull', 'Inputs Incompleted!', 'red');
        return "false";
    }
    else{
        return option_objs;
    }
}

function collect_wholesale_prices(){
    let is_partial_input = false;
    let wholesale_prices = [];
    if (!check_any_checkbox_selected()){
        response_message('Unsuccessfull', 'Inputs Incompleted!', 'red');
        return "false"
    }
    $(".row-data").each(function(){
        if (!$(this).children(".row-checkbox").children(".checkbox-table-row").is(':checked')){
            return true;
        }
        let from_data = $(this).children(".row-from").children(".from").text();
        let to_data = $(this).children(".row-to").children(".to").text();
        let price_data = $(this).children(".row-price").children(".price").text();
        if (from_data.trim().length==0 && to_data.trim().length==0 && price_data.trim().length==0){
            return true;
        }
        else if (from_data.trim().length!=0 && to_data.trim().length!=0 && price_data.trim().length!=0){
            if (parseInt(from_data)>parseInt(to_data)){
                is_partial_input = true;
                response_message('Unsuccessfull', 'Inputs Incorrect!', 'red');
                return false;
            }
            wholesale_prices.push({
                'from_quantity':parseInt(from_data),
                "to_quantity":parseInt(to_data),
                "price":parseInt(price_data)
            })
        }
        else{
            is_partial_input=true;
            response_message('Unsuccessfull', 'Inputs Incompleted!', 'red');
            return false;
        }
    });
    if (is_partial_input){
        return "false"
    }
    else if (wholesale_prices.length==0){
        response_message('Unsuccessfull', 'Inputs Incompleted!', 'red');
        return "false";
    }
    return wholesale_prices
}

function collect_select_inputs(){
    let is_any_select_empty = false;
    let select_input_ids = ["client-name-select","product-category-select","product-select"];
    let select_input_vals = [];
    for (let x=0 ; x<select_input_ids.length;x++){
        select_input_vals[x] = $("#"+select_input_ids[x]).val();
        if (select_input_vals[x]==null || select_input_vals[x]==""){
            is_any_select_empty = true;
            break
        }
    }
    if (is_any_select_empty){
        response_message('Unsuccessfull', 'Inputs Incompleted!', 'red');
        return "false";
    }
    return {
        'client_name':select_input_vals[0],
        'product_category':select_input_vals[1],
        'product_name':select_input_vals[2]
    }
}

function check_any_checkbox_selected(){
    let is_any_checked = false;
    $(".checkbox-table-row").each(function(){
        if ($(this).is(':checked')){
            is_any_checked = true;
            return false;
        }
    });
    return is_any_checked;
}

function add_row(){
    let row_num = parseInt($(".table-body").attr("data-row_count"))+1
    let markup_rows = "<tr class='row-data' id='tablerow-"+row_num.toString()+"'><td class='row-checkbox'><input class='checkbox-table-row' data-row_num='"+row_num.toString()+"' type='checkbox'/></td><td class='row-from'><div contenteditable='true' class='from editable table-input-"+row_num.toString()+"'></div></td><td class='row-to'><div contenteditable='true' class='to editable table-input-"+row_num.toString()+"'></div></td><td class='row-price'><div contenteditable='true' class='price editable table-input-"+row_num.toString()+"'></div></td><td class='dropdown'><a class='caret dropdown-toggle' data-toggle='dropdown'></a><ul class='dropdown-menu'><li><button  onclick='delete_row("+row_num.toString()+")' type='button' class='btn btn-light' style='display: inline-block;'>Delete Row</button></li></ul></td></tr>"
    $(".table-body").append(markup_rows);
    $(".table-body").attr("data-row_count",row_num.toString());
    numeric_only_event($(".table-input-"+row_num.toString()+".from"))
    numeric_only_event($(".table-input-"+row_num.toString()+".to"))
    float_values_allowance_for_div($(".table-input-"+row_num.toString()+".price"))
}

function delete_row(row_num){
    $("#tablerow-"+row_num.toString()).remove();
}

function add_option(){
    let option_num = parseInt($(".option-block").attr("data-option_count"))+1;
    let markup_options = '<div class="col-4"><div class="row option-inputs"><div class="col-9 option-block"><label >{{_("Option '+option_num.toString()+'")}}</label><input  type="text" class="form-control mt-2 option-option"></div><div class="col-2 price-block"><label >{{_("Price")}}</label><input id="option'+option_num.toString()+'-price" type="text" class="form-control mt-2 option-price"></div></div></div>'
    $("#options").append(markup_options);
    $(".option-block").attr("data-option_count",option_num.toString());
    float_values_allowance_for_input($("#option"+option_num.toString()+"-price"))
}

function response_message(title, message, color) {
    frappe.msgprint({
        title: __(title),
        indicator: color,
        message: __(message)
    });
}

function numeric_only_event(element){
    element.keypress(function(e) {
        if (isNaN(String.fromCharCode(e.which)) || e.which == 32) e.preventDefault();
    }).on('paste', function(event) {
        event.preventDefault();
    });
}

function float_values_allowance_for_input(element){
    element.keypress(function(event) {
        if (((event.which != 46 || (event.which == 46 && $(this).val() == '')) ||
                $(this).val().indexOf('.') != -1) && (event.which < 48 || event.which > 57)) {
            event.preventDefault();
        }
    }).on('paste', function(event) {
        event.preventDefault();
    })
}

function float_values_allowance_for_div(element){
    element.keypress(function(event) {
        if (((event.which != 46 || (event.which == 46 && $(this).text() == '')) ||
                $(this).text().indexOf('.') != -1) && (event.which < 48 || event.which > 57)) {
            event.preventDefault();
        }
    }).on('paste', function(event) {
        event.preventDefault();
    })
}