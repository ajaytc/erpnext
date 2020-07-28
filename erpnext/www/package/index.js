$(".quantity").keypress(function(e) {
    if (isNaN(String.fromCharCode(e.which)) || e.which == 32) e.preventDefault();
});

var CLIENT = null;
var CNAME = "";
var SELECTED_PRODUCTS = {};
var EMPTY_ITEM_SELECTED_MARKUP = '<option value=""  selected>---:---</option>';

$("#client-name-select").change(function(){
    let client_data_object = JSON.parse($(this).val().replace(/'/g, '"'));
    CNAME = client_data_object["client"];
    CLIENT = client_data_object["prod_cats"];
    let current_count = parseInt($(".product-details").attr("data-count"));
    for (let x=1;x<current_count+1;x++){
        set_category_options(x);
        release_product($(".item-select-"+x));
        // $(".item-select-"+x).attr("data-current",f);
        $(".item-select-"+x).empty().append(EMPTY_ITEM_SELECTED_MARKUP);
    }
});

$(".item-group").change(function(){
    trigger_item_group_select($(this));
});

$(".product").change(function(){
    trigger_item_change($(this));
});

function trigger_item_group_select(this_element){
    set_product_options(this_element);
    release_product($(".item-select-"+this_element.attr("data-number")));
};

function trigger_item_change(this_element){
    let earlier_item = this_element.attr("data-current");
    release_product(this_element);
    restrict_product(this_element);
    if (this_element.val()==""){
        add_changed_item_to_same_category($(".item-group-select-"+this_element.attr("data-number")).val(),earlier_item,this_element.attr("data-number"));
    }else{
        remove_this_item_from_others(this_element.val(),parseInt(this_element.attr("data-number")));
    }
};

function add_changed_item_to_same_category(category,early_item,number){
    $(".item-group").each(function(){
        if ($(this).attr("data-number")==number){
            return true;
        };
        if ($(this).val()==category){
            let item_name = CLIENT[category]["products"][early_item];
            $(".item-select-"+$(this).attr("data-number")).append('<option value="'+early_item+'">'+item_name+'</option>');
        }
    });
};

function remove_this_item_from_others(item_code,this_select){
    let current_count = parseInt($(".product-details").attr("data-count"));
    for (let x=1;x<current_count+1;x++){
        if (x!=this_select){
            let option_count = $(".item-select-"+x+" option").length;
            for (let y=0;y<option_count;y++){
                if ($(".item-select-"+x).children().eq(y).val()==item_code){
                    $(".item-select-"+x).children().eq(y).remove();
                };
            };
        }
    };
};

function restrict_product(this_element){
    let f = this_element.val();
    this_element.attr("data-current",f);
    if (f==""){
        return null;
    };
    let div_number = this_element.attr("data-number");
    if (!SELECTED_PRODUCTS.hasOwnProperty(f)){
        SELECTED_PRODUCTS[f] = [];
    };
    SELECTED_PRODUCTS[f].push(div_number); 
};

function release_product(this_element){
    let current_item = this_element.attr("data-current");
    let div_number = this_element.attr("data-number");
    let should_empty = false;
    if (SELECTED_PRODUCTS.hasOwnProperty(current_item)){
        if (SELECTED_PRODUCTS[current_item].includes(div_number)){
            SELECTED_PRODUCTS[current_item].splice(SELECTED_PRODUCTS[current_item].indexOf(div_number),1);
        };
        if (SELECTED_PRODUCTS[current_item].length==0){
            should_empty = true;
        };
    };
    if (should_empty){
        delete SELECTED_PRODUCTS[current_item];
    };

};

function set_product_options(this_ele){
    let number = this_ele.attr("data-number");
    let temp_markup =EMPTY_ITEM_SELECTED_MARKUP;
    let category = this_ele.val();
    $(".item-select-"+number).empty();
    if (category==""){
        release_product($(".item-select-"+number));
        $(".item-select-"+number).append(temp_markup);
        return null;
    };
    $.each(CLIENT[category]["products"], function(k, v){
        if (!(SELECTED_PRODUCTS.hasOwnProperty(k))){
            temp_markup = temp_markup + '<option value="'+k+'">'+v+'</option>';            
        };
    });
    $(".item-select-"+number).append(temp_markup);
}

function set_category_options(number){
    $(".item-group-select-"+number.toString()).empty();
    let temp_markup = '<option value="">---:---</option>'
    $.each(CLIENT, function(k, v){
        temp_markup = temp_markup + '<option value="'+k+'">'+v.item_group_name+'</option>'
    })
    $(".item-select-"+number.toString()).attr("data-current","")
    $(".item-group-select-"+number.toString()).append(temp_markup);
}

function add_products(){
    let items_per_row = 2;
    var markup = '<div class="row pro-row">';
    let current_count = parseInt($(".product-details").attr("data-count"));
    for (let k=1;k<items_per_row+1;k++){
        let p = (current_count+k).toString()
        let temp_markup = '<div class="col-6">\
        <div class="row">\
        <div class="col-5 group">\
                    <label>Product Category</label>\
                    <select data-number="'+p+'" class="form-control item-group form-font item-group-select-'+p+'">\
                        <option value="">---:---</option>\
                        </select>\
                </div>\
                <div class="col-5 item">\
                <label>Product</label>\
                    <select data-current="" data-number="'+p+'" class="form-font product form-control  item-select-'+p+'">\
                    '+EMPTY_ITEM_SELECTED_MARKUP+'\
                    </select>\
                    </div>\
                <div class="col-2 quantity">\
                <label>Quantity</label>\
                    <input data-number="'+p+'" type="text" class="form-font form-control quantity-'+p+'">\
                    </div>\
            </div>\
            </div>'
            markup = markup + temp_markup
    }
    markup = markup+'</div>'
    $(".product-details").attr("data-count",(items_per_row+current_count).toString());
    $(".product-details").append(markup);
    if (CLIENT!=null){
        for (let k=1;k<items_per_row+1;k++){
            set_category_options(current_count+k);
        }
    }
    bind_group_select_events(current_count,items_per_row);
    bind_item_select_events(current_count,items_per_row);
    $(".quantity").keypress(function(e) {
        if (isNaN(String.fromCharCode(e.which)) || e.which == 32) e.preventDefault();
    });
}

function bind_group_select_events(current_count,items_per_row){
    for (let k=1;k<items_per_row+1;k++){
        let l = current_count+k;
        $(".item-group-select-"+l.toString()).change(function(){
            trigger_item_group_select($(this));
        });
    };
};

function bind_item_select_events(current_count,items_per_row){
    for (let k=1;k<items_per_row+1;k++){
        let l = current_count+k;
        $(".item-select-"+l.toString()).change(function(){
            trigger_item_change($(this));
        });
    };
};


function save_products(){
    let data_result = collect_all_data();
    if (data_result.status !="ok") {
        response_message('Unsuccessfull',data_result.message, 'green');
        return null;
    };

    frappe.call({
        method: 'erpnext.modehero.product.create_package',
        args: {
            data:data_result.data
        },
        callback: function (r) {
            if (r) {
                if (r.message['status'] == "ok") {
                    response_message('Successfull', 'Package created successfully', 'green')
                    window.location.reload(true)
                    return null;
                }
                response_message('Unsuccessfull', 'Package created unsuccessfully', 'red')
                window.location.reload(true)
                return null
            }
            response_message('Unsuccessfull', 'Package created unsuccessfully', 'red')
        }
    });
}

function collect_all_data(){
    let ERROE_MESSAGE = "Please input right data !";
    let return_obj = {};
    return_obj["message"]="";
    return_obj["status"]="error";
    let client_name = $("#client-name-select").val();
    let package_name = $("#package-name").val();
    if (client_name=="" || package_name.trim().length==0){
        return_obj.message = ERROE_MESSAGE;
        return return_obj;
    };
    let product_data = collect_product_data();
    if(product_data.status!="ok"){
        return_obj.message = ERROE_MESSAGE;
        return return_obj;
    };
    return_obj.status="ok";
    return_obj["data"] = {"client":CNAME,"package_name":package_name,"product_data":product_data.data};
    return return_obj;
};

function collect_product_data(){
    let select_count = parseInt($(".product-details").attr("data-count"));
    let return_obj = {};
    return_obj["status"]="ok";
    return_obj["data"]={};
    let is_empty = true;
    for (let k=1;k<=select_count;k++){
        let is_partial= false;
        let temp_cat = $(".item-group-select-"+k.toString()).val();
        let temp_prod = $(".item-select-"+k.toString()).val();
        let temp_qnty = $(".quantity-"+k.toString()).val();
        if (temp_cat!=""){
            if (temp_prod!=""){
                if(temp_qnty.trim().length==0){
                    is_partial=true;
                }
            }else{
                is_partial=true;
            };
        };
        if (is_partial||isNaN(temp_qnty)||(return_obj.data.hasOwnProperty(temp_prod))){
            return_obj["status"] = "error";
            break;
        };
        if (temp_qnty!="" && temp_prod!="" && temp_cat!=""){
            is_empty = false;
            return_obj.data[temp_prod] = {"item_group":temp_cat,"quantity":parseInt(temp_qnty)}
        }
    };
    if (is_empty){
        return_obj["status"] = "error";
    }
    return return_obj;
};


function response_message(title, message, color) {
    frappe.msgprint({
        title: __(title),
        indicator: color,
        message: __(message)
    });
}






























































// window.onload= (event)=>{
//     $(".default-option-price").keypress(function(e) {
//         if (isNaN(String.fromCharCode(e.which))) e.preventDefault();
//     });
//     $(".modifiable-row").keypress(function(e) {
//         if (isNaN(String.fromCharCode(e.which))) e.preventDefault();
//     });
//     $(".table-input-1").keypress(function(e) {
//         if (isNaN(String.fromCharCode(e.which))) e.preventDefault();
//     });
// }

// $("#product-category-select").change(function(){
//     set_products_at_select_change();
// })


// $("#select-all-check").change(function(){
//     if ($(this).is(':checked')) {
//         $(".checkbox-table-row").prop('checked', true).change();
//     } else {
//         $(".checkbox-table-row").prop('checked', false).change();
//     }
// });



// $("#minimum-order").keypress(function(e) {
//     if (isNaN(String.fromCharCode(e.which))) e.preventDefault();
// })

// $("#modify").click(function(){
//     let form_data = collect_all_data();
//     if (form_data==null){
//         return null
//     }
//     let active_product_name = $(this).attr("ap-name")
//     frappe.call({
//         method: 'erpnext.modehero.customer.modify_pricing',
//         args: {
//             form_data:form_data,
//             name : active_product_name
//         },
//         callback: function (r) {
//             if (r) {
//                 if (r.message['status'] == "ok") {
//                     response_message('Successfull', 'Pricing Attribution updated successfully', 'green');
//                     window.location.href = "/active-products";
//                     return null;
//                 }
//                 response_message('Unsuccessfull', 'Pricing Attribution updated unsuccessfully', 'red');
//                 window.location.href = "/active-products";                
//                 return null;
//             }
//             response_message('Unsuccessfull', 'Pricing Attribution updated unsuccessfully', 'red');
//         }
//     });
// })

// $("#submit").click(function(){
//     let form_data = collect_all_data();
//     if (form_data==null){
//         return null
    // }
    // frappe.call({
    //     method: 'erpnext.modehero.customer.set_pricing',
    //     args: {
    //         form_data:form_data
    //     },
    //     callback: function (r) {
    //         if (r) {
    //             if (r.message['status'] == "ok") {
    //                 response_message('Successfull', 'Pricing Attribution created successfully', 'green')
    //                 window.location.reload(true)
    //                 return null;
    //             }
    //             response_message('Unsuccessfull', 'Pricing Attribution created unsuccessfully', 'red')
    //             window.location.reload(true)
    //             return null
    //         }
    //         response_message('Unsuccessfull', 'Pricing Attribution created unsuccessfully', 'red')
    //     }
    // });
// })

// function set_products_at_select_change(){
//     let category =  $('#product-category-select option:selected').val();
//     let client = $('#client-name-select option:selected').val();
//     if (!category){
//         return null
//     }
//     if (!client){
//         return null
//     }
//     $("#product-select").find("option").remove();
//     let prices_items = get_priced_items(client,category);
//     if (prices_items==null){
//         set_disable_option()
//         return null
//     }
//     frappe.call({
//         method: 'erpnext.modehero.product.get_priducts_of_category',
//         args: {
//             category:category
//         },
//         callback: function (r) {
//             if (!r.message) {
//                 set_disable_option()
//                 return null
//             }
//             let objects=r.message
//             let is_empty = true
//             if (objects.length>0){
//                 for (i = 0; i < objects.length; i++) {
//                     if (!(prices_items.includes(objects[i].name))){
//                         let temp_markup = '<option  value="'+objects[i].name+'">'+objects[i].item_name+'</option>';
//                         $("#product-select").append(temp_markup);
//                         is_empty = false
//                     }
//                 }
//                 if (is_empty){
//                     set_disable_option()
//                 }
//             }
//             else{
//                 set_disable_option()
//             }
//         }
//     });
// }

// function get_priced_items(client,category){
//     let priced_list = []
//     frappe.call({
//         method: 'erpnext.modehero.product.get_priced_products',
//         args: {
//             client,client,
//             category:category
//         },
//         callback: function (r) {
//             if (!r.message) {
//                 return null
//             }
//             let objects=r.message
//             if (objects.length>0){
//                 for (i = 0; i < objects.length; i++) {
//                     priced_list.push(objects[i].item_code);                    
//                 }
//             }
//             else{
//                 return []
//             }
//         }
//     });
//     return priced_list
// }

// function set_disable_option(){
//     let temp_markup = '<option  value="" disabled selected>No Product Available</option>';
//     $("#product-select").append(temp_markup);
// }

// function collect_all_data(){
//     let select_inputs = collect_select_inputs();
//     if (select_inputs=="false"){
//         return null;
//     }
//     let options = collect_options();
//     if (options=="false"){
//         return null;
//     }
//     let wholesale_prices = collect_wholesale_prices();
//     if (wholesale_prices=="false"){
//         return null;
//     }
//     let season_input = $("#season-input").val();
//     if (season_input.trim().length==0){
//         response_message('Unsuccessfull', 'Inputs Incompleted!', 'red');
//         return null;
//     }
//     let minimum_order = $("#minimum-order").val();
//     if (minimum_order.trim().length==0){
//         minimum_order = 0;
//     }
//     minimum_order = parseInt(minimum_order);
//     let show_price = false;
//     if ($("#show-price").is(':checked')) {
//         show_price = true;
//     }
//     return {
//         'pricing_options':options,
//         'wholesale_price':wholesale_prices,
//         'show_price':show_price,
//         'minimum_order':minimum_order,
//         'season':season_input,
//         'item_code':select_inputs.product_name,
//         'item_group':select_inputs.product_category,
//         'client':select_inputs.client_name
//     }
// }

// function collect_options(){
//     let option_objs = [];
//     let is_any_partial_empty = false;
//     $(".option-inputs").each(function(){
//         let option = $(this).children(".option-block").children(".option-option").val();
//         let price = $(this).children(".price-block").children(".option-price").val();

//         if (option.trim().length!=0 && price.trim().length==0){
//             is_any_partial_empty = true;
//             return false;
//         }
//         else if(option.trim().length==0 && price.trim().length!=0){
//             is_any_partial_empty = true;
//             return false;
//         }
//         else if (option.trim().length==0 && price.trim().length==0){
//             return true;
//         }
//         else{
//             option_objs.push({
//                 'option':option,
//                 'price':price
//             });
//         }
//     })
//     if (is_any_partial_empty){
//         response_message('Unsuccessfull', 'Inputs Incompleted!', 'red');
//         return "false";
//     }
//     else{
//         return option_objs;
//     }
// }

// function collect_wholesale_prices(){
//     let is_partial_input = false;
//     let wholesale_prices = [];
//     if (!check_any_checkbox_selected()){
//         response_message('Unsuccessfull', 'Inputs Incompleted!', 'red');
//         return "false"
//     }
//     $(".row-data").each(function(){
//         if (!$(this).children(".row-checkbox").children(".checkbox-table-row").is(':checked')){
//             return true;
//         }
//         let from_data = $(this).children(".row-from").children(".from").text();
//         let to_data = $(this).children(".row-to").children(".to").text();
//         let price_data = $(this).children(".row-price").children(".price").text();
//         if (from_data.trim().length==0 && to_data.trim().length==0 && price_data.trim().length==0){
//             return true;
//         }
//         else if (from_data.trim().length!=0 && to_data.trim().length!=0 && price_data.trim().length!=0){
//             if (parseInt(from_data)>parseInt(to_data)){
//                 is_partial_input = true;
//                 response_message('Unsuccessfull', 'Inputs Incorrect!', 'red');
//                 return false;
//             }
//             wholesale_prices.push({
//                 'from_quantity':parseInt(from_data),
//                 "to_quantity":parseInt(to_data),
//                 "price":parseInt(price_data)
//             })
//         }
//         else{
//             is_partial_input=true;
//             response_message('Unsuccessfull', 'Inputs Incompleted!', 'red');
//             return false;
//         }
//     });
//     if (is_partial_input){
//         return "false"
//     }
//     else if (wholesale_prices.length==0){
//         response_message('Unsuccessfull', 'Inputs Incompleted!', 'red');
//         return "false";
//     }
//     return wholesale_prices
// }

// function collect_select_inputs(){
//     let is_any_select_empty = false;
//     let select_input_ids = ["client-name-select","product-category-select","product-select"];
//     let select_input_vals = [];
//     for (let x=0 ; x<select_input_ids.length;x++){
//         select_input_vals[x] = $("#"+select_input_ids[x]).val();
//         if (select_input_vals[x]==null || select_input_vals[x]==""){
//             is_any_select_empty = true;
//             break
//         }
//     }
//     if (is_any_select_empty){
//         response_message('Unsuccessfull', 'Inputs Incompleted!', 'red');
//         return "false";
//     }
//     return {
//         'client_name':select_input_vals[0],
//         'product_category':select_input_vals[1],
//         'product_name':select_input_vals[2]
//     }
// }

// function check_any_checkbox_selected(){
//     let is_any_checked = false;
//     $(".checkbox-table-row").each(function(){
//         if ($(this).is(':checked')){
//             is_any_checked = true;
//             return false;
//         }
//     });
//     return is_any_checked;
// }

// function add_row(){
//     let row_num = parseInt($(".table-body").attr("data-row_count"))+1
//     let markup_rows = "<tr class='row-data' id='tablerow-"+row_num.toString()+"'><td class='row-checkbox'><input class='checkbox-table-row' data-row_num='"+row_num.toString()+"' type='checkbox'/></td><td class='row-from'><div contenteditable='true' class='from editable table-input-"+row_num.toString()+"'></div></td><td class='row-to'><div contenteditable='true' class='to editable table-input-"+row_num.toString()+"'></div></td><td class='row-price'><div contenteditable='true' class='price editable table-input-"+row_num.toString()+"'></div></td><td class='dropdown'><a class='caret dropdown-toggle' data-toggle='dropdown'></a><ul class='dropdown-menu'><li><button  onclick='delete_row("+row_num.toString()+")' type='button' class='btn btn-light' style='display: inline-block;'>Delete Row</button></li></ul></td></tr>"
//     $(".table-body").append(markup_rows);
//     $(".table-body").attr("data-row_count",row_num.toString());
//     $(".table-input-"+row_num.toString()).keypress(function(e) {
//         if (isNaN(String.fromCharCode(e.which))) e.preventDefault();
//     });
// }

// function delete_row(row_num){
//     $("#tablerow-"+row_num.toString()).remove();
// }

// function add_option(){
//     let option_num = parseInt($(".option-block").attr("data-option_count"))+1;
//     let markup_options = '<div class="col-4"><div class="row option-inputs"><div class="col-9 option-block"><label >{{_("Option '+option_num.toString()+'")}}</label><input  type="text" class="form-control mt-2 option-option"></div><div class="col-2 price-block"><label >{{_("Price")}}</label><input id="option'+option_num.toString()+'-price" type="text" class="form-control mt-2 option-price"></div></div></div>'
//     $("#options").append(markup_options);
//     $(".option-block").attr("data-option_count",option_num.toString());
//     $("#option"+option_num.toString()+"-price").keypress(function(e) {
//         if (isNaN(String.fromCharCode(e.which))) e.preventDefault();
//     });
// }

// function response_message(title, message, color) {
//     frappe.msgprint({
//         title: __(title),
//         indicator: color,
//         message: __(message)
//     });
// }