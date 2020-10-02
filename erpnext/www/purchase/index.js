var SUPPLY_TABLE = '<div class="table-wrapper table-responsive mt-2">\
                        <table class="table table-sm table-striped">\
                            <thead class="thead-supply-table">\
                                <th></th>\
                                <th>Destination</th>\
                                <th>Product</th>\
                                <th>Number of pieces</th>\
                                <th>Consumption per piece</th>\
                                <th>Total consumption</th>\
                                <th>Safety margin (%)</th>\
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
var SUPPLY_CONTENT = {}
var SELECTED_ITEM_FACTORY_DETAILS = {}
var SALES_ORDER_DETAILS = {}
var SUPPLY_ORDER_DETAILS = {}
var IS_SUPPLY_BUTTONS= false
var REMINDER_INPUTS = {}
var SUPPLY_TYPES = ["fabric","trimming","packaging"]

window.onload = function(){
    $('.sum-quantity').each(function(){
        let item = $(this).attr('data-item');
        let size = $(this).attr('data-size');
        let sum = get_sum(item,size);
        $(this).text(sum);
    })
    $('.total-sum').each(function(){
        let item = $(this).attr('data-item');
        let total_sum = get_total_sum(item);
        $(this).text("Total : "+total_sum.toString());
    })
    $(".default-hide").hide().find('input').prop('disabled', true)
    sort_select( $(".factory-select"))
}

$(".select-button").click(async function(){
    let item = $(this).attr("data-item")
    if ($(this).hasClass("not-selected")){
        let is_selected = await select(item).then()
        if (is_selected){
            $(this).removeClass("not-selected").addClass("selected")
        }
    }else if ($(this).hasClass("selected")){
        $(this).removeClass("selected").addClass("not-selected")
        remove_item(item)
        delete SELECTED_ITEM_FACTORY_DETAILS[item]
        delete SALES_ORDER_DETAILS[item]
        if (Object.keys(SELECTED_ITEM_FACTORY_DETAILS).length==0){
            IS_SUPPLY_BUTTONS = false
            $("#supply-button-section").empty()
        }
    }
})

$(".factory-select").change( async function(){
    let item = $(this).attr("data-item_code")
    if ($(".select-button[data-item|='"+item+"']").hasClass("not-selected")){
        return null
    }
    let current_factory = $(this).val()
    if (current_factory!=""){
        remove_item(item)
        let order = {"factory_name":$("option[value|='"+current_factory+"']").attr("data-factory_name") ,"factory":current_factory,"order":SALES_ORDER_DETAILS[item]["order"]}
        let is_set_supply_section = await set_supply_order_section(item,order)
        if (!is_set_supply_section){
            SELECTED_ITEM_FACTORY_DETAILS[item] = current_factory
        }
    }
})

$(".client-modal-link").click(function(){
    let data_array = ["country","city","phone","email","cusname"];
    for (let k=0;k<data_array.length;k++){
        $("#modal-"+data_array[k]).text($(this).attr("data-"+data_array[k]));
    }
    $("#client-modal").modal('show');
});

function open_reminder_modal(destination,supply,supplier){
    $("#reminder-modal").attr("data-destination",destination)
    $("#reminder-modal").attr("data-supply",supply)
    $("#reminder-modal").attr("data-supplier",supplier)
    $("#reminder-modal").modal('show');
    let empty_rem = false
    if (!REMINDER_INPUTS.hasOwnProperty(supply)){
        empty_rem = true
    }else if(!REMINDER_INPUTS[supply].hasOwnProperty(destination)){
        empty_rem = true
    }else if(!REMINDER_INPUTS[supply][destination].hasOwnProperty(supplier)){
        empty_rem = true
    }
    if (empty_rem){
        $("input.date-picker").each(function(){
            $(this).val("");
            $(this).siblings('span.selected_value').text("")
            $(this).removeClass('active')
        })
    }else{
        $("input.date-picker").each(function(){
            $(this).val(REMINDER_INPUTS[supply][destination][supplier][this.name]);
            $(this).siblings('span.selected_value').text(REMINDER_INPUTS[supply][destination][supplier][this.name])
            $(this).addClass('active');
        })
    }
}

$("#add-reminder-button").click(function(){
    let reminder_values = {}
    let supply = $("#reminder-modal").attr("data-supply")
    let destination  = $("#reminder-modal").attr("data-destination")
    let supplier = $("#reminder-modal").attr("data-supplier")
    $("input.date-picker").each(function(){
        reminder_values[this.name] = $(this).val();
    })
    if (!REMINDER_INPUTS.hasOwnProperty(supply)){
        REMINDER_INPUTS[supply] = {}
        REMINDER_INPUTS[supply][destination]={}
        REMINDER_INPUTS[supply][destination][supplier] = reminder_values
    }else if(!REMINDER_INPUTS[supply].hasOwnProperty(destination)){
        REMINDER_INPUTS[supply][destination]={}
        REMINDER_INPUTS[supply][destination][supplier] = reminder_values
    }
    REMINDER_INPUTS[supply][destination][supplier] = reminder_values
    
})

$("input[type='checkbox'].sales-order-section").change(function(){
    if($(this).attr('data-check_type')=="select-all"){
        return null
    }
    if ($(this).is(':checked')){
        $("."+ $(this).attr('data-order_count')+"-qnty-content-class").each(function(){
            numeric_only_event($(this).attr('contenteditable','true'))
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

$("#product-only-confirmation-button").click(function(){
    frappe.call({
        method: 'erpnext.modehero.sales_order.validate_products_only',
        args: {
            order_bloc_object:SALES_ORDER_DETAILS
        },
        callback: function (r) {
            if (r) {
                if (r.message['status'] == "ok") {
                    response_message('Successfull', r.message['message'] , 'green')
                    window.location.reload()
                    return null;
                }
                response_message('Unsuccessfull',r.message['message'], 'red')
                window.location.reload()
                return null
            }
            response_message('Unsuccessfull', 'Orders validated unsuccessfully', 'red')
        }
    });
})

$("#product-supply-confirmation-button").click(function(){
    frappe.call({
        method: 'erpnext.modehero.sales_order.validate_products_supply',
        args: {
            sales_orders:SALES_ORDER_DETAILS,
            supply_orders:SUPPLY_ORDER_DETAILS
        },
        callback: function (r) {
            if (r) {
                if (r.message['status'] == "ok") {
                    response_message('Successfull', r.message['message'], 'green')
                    window.location.reload()
                    return null;
                }
                response_message('Unsuccessfull',r.message['message'], 'red')
                window.location.reload()
                return null
            }
            response_message('Unsuccessfull', 'Orders validated unsuccessfully.', 'red')
        }
    });
})

function set_modify(item){
    $('.modify-show-'+item).show().find('input').prop('disabled', false)
    $('.modify-hide-'+item).hide().find('input').prop('disabled', true)
}

function cancel_modify(item){
    $('input:checkbox.sales-order-section').prop('checked', false).change();
    $('.modify-show-'+item).hide().find('input').prop('disabled', true)
    $('.modify-hide-'+item).show().find('input').prop('disabled', false)
}

function validate_product_and_supply(){
    if (is_any_supply_check()){
        validate_product_only()
        return null
    }
    let supply_order_details = collect_data_for_supply()
    if (supply_order_details==null){
        response_message('Unsuccessfull', 'Incompleted inpput.', 'red')
        return null
    }
    SUPPLY_ORDER_DETAILS = supply_order_details
    $("#product-supply-confirmation-modal-body").text("You have selected only "+Object.keys(SALES_ORDER_DETAILS).length+" order blocks and supply orders from "+Object.keys(SUPPLY_ORDER_DETAILS).length +" supply. Are you sure want to confirm?")
    $("#product-supply-confirmation-modal").modal("show")
}

function validate_product_only(){
    let item_amount = Object.keys(SALES_ORDER_DETAILS).length
    if (item_amount==0){
        return null
    }
    $("#product-only-confirmation-modal-body").text("You have selected only "+item_amount+" order blocks and no supply. Are you sure want to confirm?")
    $("#product-only-confirmation-modal").modal("show")
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
                    response_message('Successfull', 'Orders updated successfully !', 'green')
                    window.location.reload()
                    return null;
                }
                response_message('Unsuccessfull', 'Orders not updated successfully !', 'red')
                window.location.reload()
                return null
            }
            response_message('Unsuccessfull', 'Orders updated unsuccessfully !', 'red')
        }
    });
}

async function select(item){
    let order = collect_data_for_select(item);
    if (order==null){
        response_message('Unsuccessfull', 'Incomplete data !', 'red')
        return false
    }
    else if(order=="factory_error"){
        response_message('Unsuccessfull', 'Factory is not selected !', 'red')
        return false
    }
    // let selected = check_already_selected(item,order.factory)
    // if (selected.status){
    //     return false
    // }
    let is_set_supply_section = await set_supply_order_section(item,order)
    if (!is_set_supply_section){
        return false
    }
    if (!IS_SUPPLY_BUTTONS){
        IS_SUPPLY_BUTTONS = true
        add_validate_buttons()
    }
    SALES_ORDER_DETAILS[item] = order
    SELECTED_ITEM_FACTORY_DETAILS[item] = order.factory
    return true
}

function cancel(item){
    let orders = []
    $("tr[data-item_code|='"+item+"']").each(function(){
        let order_name = $(this).attr('data-order');
        orders.push(order_name);
    })

    $('input:checkbox.sales-order-section').prop('checked', false);
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

function collect_data_for_select(item){
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
    $('input:checkbox.sales-order-section').prop('checked', false).change();
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
            return false
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

    $('input:checkbox.sales-order-section').prop('checked', false).change();
    if (is_any_empty){
        return null
    }
    if(Object.keys(order).length==0){
        return null
    }
    return order
}

function collect_data_for_supply(){
    let supply_details = {}
    let is_any_wrong_input = false
    $("input:checkbox.supply-section").each(function(){
        if (!$(this).is(':checked')){
            return 
        }
        let destination = $(this).attr("data-destination")
        let supply = $(this).attr("data-supply")
        let vendor = $(this).attr("data-supplier")
        if (destination.trim().length==0 || supply.trim().length==0 || vendor.trim().length==0 || SUPPLY_TYPES.indexOf($(this).parent().parent().attr("data-supply_group"))==-1){
            is_any_wrong_input = true
            return false
        }
        if (!supply_details.hasOwnProperty(supply)){
            supply_details[supply] = {"supply_group":$(this).parent().parent().attr("data-supply_group"),"destinations":{}}
        }
        if (!supply_details[supply]["destinations"].hasOwnProperty(destination)){
            supply_details[supply]["destinations"][destination] = {}
        }
        order = get_supply_order_detail($(this).parent().parent(),destination,supply,vendor)
        if (order==null ){
            is_any_wrong_input = true
            return false
        }
        supply_details[supply]["destinations"][destination][vendor] = order
    })
    if(is_any_wrong_input){
        return null
    }
    return supply_details
}

function is_any_supply_check(){
    let is_any_checked = true
    $("input:checkbox.supply-section").each(function(){
        if ($(this).is(':checked')){
            is_any_checked = false;
            return false
        }
    })
    return is_any_checked
}

function get_supply_order_detail(table_row,destination,supply,vendor){
    let order = {}
    order["products"] = get_products_of_supply_rows(table_row,destination,supply,vendor)
    order["theoritical_order"] = table_row.children(".to-supply-product").text()
    order["minimum_oq"] = table_row.children(".moq-supply-product").text()
    order["order_count"] = table_row.children(".order-supply-product").children("span").text()
    order["internal_ref"] = table_row.children(".if-supply-product").children("span").text()
    if (REMINDER_INPUTS.hasOwnProperty(supply)&& REMINDER_INPUTS[supply].hasOwnProperty(destination) &&  REMINDER_INPUTS[supply][destination].hasOwnProperty(vendor)){
        order["reminder"] = REMINDER_INPUTS[supply][destination][vendor]
    }else{
        order["reminder"] = {"proforma_date":"","confirmation_date":"","payment_date":"","reception_date":"","shipment_date":""}
    }
    let validated = true
    for(let key in order){
        if (key=="reminder"||key=="products"){
            continue
        }
        if ( order[key].trim().length==0 ||(key =="order_count" && isNaN(order[key]))){
            validated = false
            break
        }
    }
    if(!validated){
        return null
    }
    return order
}

function get_products_of_supply_rows(table_row,destination,supply,vendor){
    let product_list =[]
    if (table_row.hasClass("data-row")){
        product_list.push(table_row.attr("data-suppliere_row_item"))
    }else if (table_row.hasClass("summary-row")){
        table_row.parent().children(".data-row[data-destination|='"+destination+"'][data-supplier|='"+vendor+"']").each(function(){
            product_list.push($(this).attr("data-suppliere_row_item"))
        })
    }
    return product_list
}

function remove_item(item){
    // here factory is earlier selecte factory
    $(".data-row[data-suppliere_row_item|='"+item+"']").remove()
    for (let supply in SUPPLY_CONTENT){
        for (let destination in SUPPLY_CONTENT[supply]){
            for (let vendor in SUPPLY_CONTENT[supply][destination]){
                if (!SUPPLY_CONTENT[supply][destination][vendor]["items"].includes(item) ){
                    continue
                }
                SUPPLY_CONTENT[supply][destination][vendor]["items"].splice(SUPPLY_CONTENT[supply][destination][vendor]["items"].indexOf(item), 1)
                SUPPLY_CONTENT[supply][destination][vendor]["count"] = SUPPLY_CONTENT[supply][destination][vendor]["count"]-1
                if (SUPPLY_CONTENT[supply][destination][vendor]["count"]==0){
                    if (REMINDER_INPUTS[supply] && REMINDER_INPUTS[supply][destination]  ){
                        delete REMINDER_INPUTS[supply][destination][vendor]
                    }
                    delete SUPPLY_CONTENT[supply][destination][vendor]
                    $(".supply-block[data-supply|='"+supply+"'] > .table-wrapper > table > .tbody-supply-order-section > .summary-row[data-destination|='"+destination+"'][data-supplier|='"+vendor+"']").remove()
                }
                else if(SUPPLY_CONTENT[supply][destination][vendor]["count"]==1){
                    if ($(".supply-block[data-supply|='"+supply+"'] > .table-wrapper > table > .tbody-supply-order-section > .summary-row[data-destination|='"+destination+"'][data-supplier|='"+vendor+"']").length!=0){
                        $(".supply-block[data-supply|='"+supply+"'] > .table-wrapper > table > .tbody-supply-order-section > .summary-row[data-destination|='"+destination+"'][data-supplier|='"+vendor+"']").remove()
                        let k  = $(".supply-block[data-supply|='"+supply+"'] > .table-wrapper > table > .tbody-supply-order-section > .data-row[data-destination|='"+destination+"'][data-supplier|='"+vendor+"']")
                        k.children(".order-supply-product").append('<span class="background-ash numeric-editable" contenteditable="true"> </span>')
                        k.children(".if-supply-product").append('<span class="background-ash" contenteditable="true"> </span>')        
                        k.children(".select-box-supply-product").append('<input data-supply="'+supply+'"   data-destination="'+destination+'"  data-supplier="'+vendor+'" class="supply-order-checkbox not-summary-box supply-section" type="checkbox"/>')
                        k.children(".reminder-supply-product").append('<div class="reminder-link" onclick="open_reminder_modal(\''+destination+'\',\''+supply+'\',\''+vendor+'\')">Reminder</div>')
                    }
                }else{
                    $(".supply-block[data-supply|='"+supply+"'] > .table-wrapper > table > .tbody-supply-order-section > .data-row[data-destination|='"+destination+"'][data-supplier|='"+vendor+"']").children(".sm-supply-product").children(".numeric-editable").last().trigger("input")
                }
            }
            if (Object.keys(SUPPLY_CONTENT[supply][destination]).length==0){
                delete SUPPLY_CONTENT[supply][destination]
            }
        }
        if (Object.keys(SUPPLY_CONTENT[supply]).length==0){
            delete SUPPLY_CONTENT[supply]
            $(".supply-block[data-supply|='"+supply+"']").remove()
        }
    }
    numeric_only_event($(".numeric-editable"))
}

async function set_supply_order_section(item,order){
    let total_order_count = await get_total_order_detail(order)
    if (total_order_count==null){
        return false
    }
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
        await change_supplier_division(item_details,order,total_order_count)
        return true
    }
    return false
}

async function change_supplier_division(item,order,total_order_count){
    let supplieres = item.supplier
    for (let i=0;i<supplieres.length;i++){
        let supply_type = supplieres[i].supplier_group.toLowerCase()
        let supply_ref = await get_supply_item_ref(supplieres[i])
        let supply_detail = await get_supply_details(supply_ref,supply_type).then()
        if (supply_detail==null){
            continue
        }
        await create_supply_table_head(supply_detail)
        if (!SUPPLY_CONTENT.hasOwnProperty(supply_detail.name)){
            SUPPLY_CONTENT[supply_detail.name] = {}
        }
        let tbody_element = $(".supply-block[data-supply|='"+supply_detail.name+"'] > .table-wrapper > table > .tbody-supply-order-section")
        await add_supply_block_table_body(tbody_element,supply_detail,supply_type,supplieres[i],item,order,total_order_count)
    }
    numeric_only_event($(".numeric-editable"))
}

async function create_supply_table_head(supply_detail){
    if ($(".supply-block[data-supply|='"+supply_detail.name+"']").length==0){
        let markup = '<div class="supply-block" data-supply="'+supply_detail.name+'" >\
                        <h3>'+supply_detail.name+'</h3>\
                      </div>'
        $("#supply-content-section").append(markup)
        $(".supply-block[data-supply|='"+supply_detail.name+"']").append(SUPPLY_TABLE)
    }
}

async function add_supply_block_table_body(tbody_element,supply_detail,supply_type,item_supplier_obj,item,order,total_order_count){
    let consumption_per_piece = await get_consumption(item_supplier_obj,supply_type).then()
    // if (consumption_per_piece==null){
    //     return null
    // }
    let moq = supply_detail.minimum_order_qty
    if (!moq){
        moq = 0
    }
    let destination = order.factory
    let vendor = item_supplier_obj.supplier
    let markup = '\
    <tr class="data-row" data-supplier="'+vendor+'" data-supply_group="'+supply_type+'" data-suppliere_row_item="'+item.name+'"  data-destination="'+destination+'">\
        <td class="select-box-supply-product"><input data-supply="'+supply_detail.name+'"   data-destination="'+destination+'"  data-supplier="'+vendor+'" class="supply-order-checkbox not-summary-box supply-section" type="checkbox"/></td>\
        <td class="destination-supply-product">'+order.factory_name+'</td>\
        <td class="product-supply-product">'+item.item_name+'</td>\
        <td class="nop-supply-product">'+total_order_count+'</td>\
        <td class="cpp-supply-product">'+consumption_per_piece+'</td>\
        <td class="tc-supply-product">'+Number(consumption_per_piece)*Number(total_order_count)+'</td>\
        <td class="sm-supply-product" ><span class="background-ash numeric-editable" contenteditable="true">5</span></td>\
        <td class="to-supply-product">'+(Number(consumption_per_piece)*Number(total_order_count)*1.05).toFixed(2)+'</td>\
        <td class="moq-supply-product">'+moq+'</td>\
        <td class="order-supply-product" ><span class="background-ash numeric-editable" contenteditable="true"> </span></td>\
        <td class="sad-supply-product">0</td>\
        <td class="if-supply-product" ><span class="background-ash" contenteditable="true"> </span></td>\
        <td class="reminder-supply-product"><div class="reminder-link" onclick="open_reminder_modal(\''+destination+'\',\''+supply_detail.name+'\',\''+vendor+'\')">Reminder</div></td>\
    </tr>'
    if(!SUPPLY_CONTENT[supply_detail.name].hasOwnProperty(destination)){
        SUPPLY_CONTENT[supply_detail.name][destination] = {} 
    }
    if (!SUPPLY_CONTENT[supply_detail.name][destination].hasOwnProperty(vendor)){
        SUPPLY_CONTENT[supply_detail.name][destination][vendor] = {"items":[item.name],"count":1}
        tbody_element.append(markup)
        tbody_element.children(".data-row[data-destination|='"+destination+"'][data-supplier|='"+vendor+"']").children(".sm-supply-product").children(".numeric-editable").on('input',function(e){
            set_theoritical_order_of_row(tbody_element,$(this),Number(consumption_per_piece)*Number(total_order_count),destination,vendor)
        })
    }else{
        SUPPLY_CONTENT[supply_detail.name][destination][vendor]["items"].push(item.name)
        SUPPLY_CONTENT[supply_detail.name][destination][vendor]["count"] = SUPPLY_CONTENT[supply_detail.name][destination][vendor]["count"] + 1
        tbody_element.children(".data-row[data-destination|='"+destination+"'][data-supplier|='"+vendor+"']").last().after(markup)
        tbody_element.children(".data-row[data-destination|='"+destination+"'][data-supplier|='"+vendor+"']").last().children(".sm-supply-product").children(".numeric-editable").on('input',function(e){
            set_theoritical_order_of_row(tbody_element,$(this),Number(consumption_per_piece)*Number(total_order_count),destination,vendor)
        })
        let to = await empty_rows(destination,tbody_element,vendor).then()
        if (tbody_element.children(".summary-row[data-destination|='"+destination+"']").length==0){
            add_summary_row(tbody_element,destination,0,moq,to,supply_detail,supply_type,vendor)
        }else{
            tbody_element.children(".data-row[data-destination|='"+destination+"']").last().children(".sm-supply-product").children(".numeric-editable").trigger("input")
        }
    }
}
async function empty_rows(destination,tbody_element,vendor){
    let to = 0
    tbody_element.children(".data-row[data-destination|='"+destination+"'][data-supplier|='"+vendor+"']").each(function(){
        $(this).children(".order-supply-product").empty()
        $(this).children(".reminder-supply-product").empty() 
        $(this).children(".if-supply-product").empty()        
        $(this).children(".select-box-supply-product").empty() 
        to = to + Number($(this).children(".to-supply-product").text())
    })
    return to
}

function add_summary_row(tbody_element,destination,stock,moq,to,supply_detail,supply_type,vendor){

    let markup = '\
    <tr class="summary-row" data-supplier="'+vendor+'" data-supply_group="'+supply_type+'" data-destination="'+destination+'">\
        <td class="select-box-supply-product"><input data-supplier="'+vendor+'" data-supply="'+supply_detail.name+'"   data-destination="'+destination+'" class="supply-order-checkbox summary-box supply-section" type="checkbox"/></td>\
        <td class="destination-supply-product"></td>\
        <td class="product-supply-product"></td>\
        <td class="nop-supply-product"></td>\
        <td class="cpp-supply-product"></td>\
        <td class="tc-supply-product"></td>\
        <td class="sm-supply-product" ></td>\
        <td class="to-supply-product">'+to.toFixed(2)+'</td>\
        <td class="moq-supply-product">'+moq+'</td>\
        <td class="order-supply-product" ><span class="background-ash numeric-editable" contenteditable="true"> </span></td>\
        <td class="sad-supply-product">'+stock+'</td>\
        <td class="if-supply-product" ><span class="background-ash" contenteditable="true"> </span></td>\
        <td class="reminder-supply-product"><div class="reminder-link" onclick="open_reminder_modal(\''+destination+'\',\''+supply_detail.name+'\',\''+vendor+'\')">Reminder</div></td>\
    </tr>'
    tbody_element.children(".data-row[data-destination|='"+destination+"'][data-supplier|='"+vendor+"']").last().after(markup)
}


async function get_supply_details(supply_ref,supply_type){
    let suppliere = null
    await frappe.call({
        method: 'erpnext.modehero.supplier.get_supply_doc',
        args: {
            supply_ref:supply_ref,
            supply_type:supply_type
        },
        callback: function (r) {
            if (!r.exc) {
                suppliere= r.message
                return null
            }
            response_message('Unsuccessfull', 'Error !', 'red')
            return null
        }
    });
    return suppliere
}


async function get_supply_item_ref(item_supplier_obj){
    let type = item_supplier_obj.supplier_group
    let supp_item = null
    if (type=="Packaging"){
        supp_item = item_supplier_obj.packaging_ref
    }else if (type=="Trimming"){
        supp_item = item_supplier_obj.trimming_ref
    }else if (type=="Fabric"){
        supp_item = item_supplier_obj.fabric_ref
    }
    if (supp_item==null || supp_item ==""){
        return null
    }else{
        return supp_item
    }
}

function set_theoritical_order_of_row(tbody_element,this_element,total_consumption,destination,vendor){
    let rate = Number(this_element.text())
    this_element.parent().parent().children(".to-supply-product").text(((rate+100)/100*total_consumption).toFixed(2))
    let to = 0
    tbody_element.children(".data-row[data-destination|='"+destination+"'][data-supplier|='"+vendor+"']").each(function(){
        to = to + Number($(this).children(".to-supply-product").text())
    })
    tbody_element.children(".summary-row[data-destination|='"+destination+"'][data-supplier|='"+vendor+"']").children(".to-supply-product").text(to.toFixed(2))
}

async function get_consumption(item_supplier_obj,type){
    let cpp = null
    if (type=="packaging"){
        cpp = item_supplier_obj.packaging_consumption
    }else if (type=="trimming"){
        cpp = item_supplier_obj.trimming_consumption
    }else if (type=="fabric"){
        cpp = item_supplier_obj.fabric_consumption
    }
    if (cpp==null || cpp ==""){
        return null
    }else{
        return cpp
    }
}

async function get_stock(item_supplier_obj){
    let stock = null
    let supplier_ref =  await get_supply_item_ref(item_supplier_obj)
    await frappe.call({
        method: 'erpnext.modehero.stock.get_stock',
        args: {
            item_type:item_supplier_obj.supplier_group.toLowerCase(),
            ref:supplier_ref
        },
        callback: function (r) {
            if (!r.exc) {
                stock= r.message
                return null
            }
            response_message('Unsuccessfull', 'Error !', 'red')
            return null
        }
    });
    return stock.quantity
}

async function get_total_order_detail(order){
    let sales_order_collection = []
    for (const sales_order_item in order.order){
        sales_order_collection.push(sales_order_item)
    }
    let total_prodcts = null
    await frappe.call({
        method: 'erpnext.modehero.sales_order.get_total_products',
        args: {
            order_list:sales_order_collection
        },
        callback: function (r) {
            if (!r.exc) {
                total_prodcts= r.message
                return null
            }
            response_message('Unsuccessfull', 'Error !', 'red')
            return null
        }
    });
    return total_prodcts
}

function check_already_selected(item,factory){
    if(SELECTED_ITEM_FACTORY_DETAILS.hasOwnProperty(item) && SELECTED_ITEM_FACTORY_DETAILS[item]==factory){
        return {"status":true}
    }
    let earlier = SELECTED_ITEM_FACTORY_DETAILS[item]
    SELECTED_ITEM_FACTORY_DETAILS[item]=factory
    return {"status":false ,"earlier":earlier}
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

function add_validate_buttons(){
 $("#supply-button-section").append(
    '<button  onclick="validate_product_and_supply()" type="button" class="btn btn-light" style="display: inline-block;">Validate product and supply</button>\
    <button  onclick="validate_product_only()" type="button" class="btn btn-light" style="display: inline-block;">Validate product only</button>')
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
    });
}

function sort_select(select_element){
    select_element.each(function(){
        let options = $(this).children("option[value!='']")
        options.detach().sort(function(a,b) {      
            let at = $(a).text().toLowerCase();
            let bt = $(b).text().toLowerCase();         
            return (at > bt)?1:((at < bt)?-1:0);            
        });
        options.appendTo($(this)); 
    })
}