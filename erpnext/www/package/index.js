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











