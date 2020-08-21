var SUPPLY_TABLE = '<div class="table-wrapper table-responsive mt-2">\
                        <table class="table table-sm table-striped">\
                            <thead>\
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
var ORDER_DETAILS = {}
var IS_SUPPLY_BUTTONS= false
var REMINDER_INPUTS = {}

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

$(".select-button").click(async function(){
    let item = $(this).attr("data-item")
    if ($(this).hasClass("not-selected")){
        let is_selected = await select(item).then()
        if (is_selected){
            $(this).removeClass("not-selected").addClass("selected").css("background-color", "#8a7c7c")
        }
    }else if ($(this).hasClass("selected")){
        $(this).removeClass("selecte").addClass("not-selected").css("background-color", "#ddd")
        let early_selected_factory = SELECTED_ITEM_FACTORY_DETAILS[item]
        remove_item_factory(item,early_selected_factory)
        delete SELECTED_ITEM_FACTORY_DETAILS[item]
        delete ORDER_DETAILS[item]
        if (Object.keys(SELECTED_ITEM_FACTORY_DETAILS).length==0){
            IS_SUPPLY_BUTTONS = false
            $("#supply-button-section").empty()
        }
    }
})

$(".factory-select").change(function(){
    let item = $(this).attr("data-item_code")
    if ($(".select-button[data-item|='"+item+"']").hasClass("not-selected")){
        return null
    }
    let early_selected_factory = SELECTED_ITEM_FACTORY_DETAILS[item]
    let current_factory = $(this).val()
    if (early_selected_factory!=undefined && current_factory!="" && ORDER_DETAILS[item]!=undefined){
        remove_item_factory(item,early_selected_factory)
        SELECTED_ITEM_FACTORY_DETAILS[item] = current_factory
        let order = {"factory_name":$("option[value|='"+current_factory+"']").attr("data-factory_name") ,"factory":current_factory,"order":ORDER_DETAILS[item]["order"]}
        set_supply_order_section(item,order)
    }
})

$(".client-modal-link").click(function(){
    let data_array = ["country","city","phone","email","cusname"];
    for (let k=0;k<data_array.length;k++){
        $("#modal-"+data_array[k]).text($(this).attr("data-"+data_array[k]));
    }
    $("#client-modal").modal('show');
});

// $("#cancel-confirmation-modal").click(function(){
//     window.location.reload()
// })

$("#add-reminder-button").click(function(){
    let reminder_values = {}
    $("input.date-picker").each(function(){
        reminder_values[this.name] = $(this).val();
    })
    REMINDER_INPUTS[$("#reminder-modal").attr("data-supply")] = {}
    REMINDER_INPUTS[$("#reminder-modal").attr("data-supply")][$("#reminder-modal").attr("data-destination")] = reminder_values
})

$("input[type='checkbox'].sales-order-section").change(function(){
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

$("#product-only-confirmation-button").click(function(){
    frappe.call({
        method: 'erpnext.modehero.sales_order.validate_products_only',
        args: {
            order_bloc_object:ORDER_DETAILS
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
})

function open_reminder_modal(destination,supply){
    $("#reminder-modal").attr("data-destination",destination)
    $("#reminder-modal").attr("data-supply",supply)
    $("#reminder-modal").modal('show');
}

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

}

function validate_product_only(){
    let item_amount = Object.keys(ORDER_DETAILS).length
    if (item_amount==0){
        return null
    }
    $("#product-only-confirmation-modal-body").text("You have selected "+item_amount+" order blocks. Are you sure want to confirm?")
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
    let selected = check_already_selected(item,order.factory)
    if (selected.status){
        return false
    }
    let is_set_supply_section = await set_supply_order_section(item,order)
    if (!is_set_supply_section){
        return false
    }
    if (!IS_SUPPLY_BUTTONS){
        IS_SUPPLY_BUTTONS = true
        add_validate_buttons()
    }
    ORDER_DETAILS[item] = order
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

function remove_item_factory(item,factory){
    // here factory is earlier selecte factory
    $(".data-row[data-destination|='"+factory+"'][data-suppliere_row_item|='"+item+"']").remove()
    for (let supply in SUPPLY_CONTENT){
        for (let destination in SUPPLY_CONTENT[supply]){
            if (destination==factory && SUPPLY_CONTENT[supply][destination]["items"].includes(item) ){
                SUPPLY_CONTENT[supply][destination]["items"].splice(SUPPLY_CONTENT[supply][destination]["items"].indexOf(item), 1)
                SUPPLY_CONTENT[supply][destination]["count"] = SUPPLY_CONTENT[supply][destination]["count"]-1
            }
            if (SUPPLY_CONTENT[supply][destination]["count"]==0){
                if (REMINDER_INPUTS[supply] ){
                    delete REMINDER_INPUTS[supply][destination] 
                }
                delete SUPPLY_CONTENT[supply][destination]
                $(".supply-block[data-supply|='"+supply+"'] > .table-wrapper > table > .tbody-supply-order-section > .summary-row[data-destination|='"+factory+"']").remove()
            }else if(SUPPLY_CONTENT[supply][destination]["count"]==1){
                if ($(".supply-block[data-supply|='"+supply+"'] > .table-wrapper > table > .tbody-supply-order-section > .summary-row[data-destination|='"+factory+"']").length!=0){
                    $(".supply-block[data-supply|='"+supply+"'] > .table-wrapper > table > .tbody-supply-order-section > .summary-row[data-destination|='"+factory+"']").remove()
                    let k  = $(".supply-block[data-supply|='"+supply+"'] > .table-wrapper > table > .tbody-supply-order-section > .data-row[data-destination|='"+factory+"']")
                    k.children(".order-supply-prodcut").append('<span class="background-ash" contenteditable="true"> </span>')
                    k.children(".if-supply-product").append('<span class="background-ash" contenteditable="true"> </span>')        
                    k.children(".select-box-supply-product").append('<input type="checkbox"/>')
                    k.children(".reminder-supply-product").append('<div class="reminder-link" onclick="open_reminder_modal(\''+destination+'\',\''+supply+'\')">Reminder</div>')
                }
            }else{
                $(".supply-block[data-supply|='"+supply+"'] > .table-wrapper > table > .tbody-supply-order-section > .data-row[data-destination|='"+factory+"']").children(".sm-supply-product").children(".numeric-editable").last().trigger("input")
            }
            if (Object.keys(SUPPLY_CONTENT[supply]).length==0){
                delete SUPPLY_CONTENT[supply]
                $(".supply-block[data-supply|='"+supply+"']").remove()
            }
        }
    }
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
    $(".numeric-editable").keypress(function(e) {
        if (isNaN(String.fromCharCode(e.which)) || e.which == 32) e.preventDefault();
    });
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
    if (consumption_per_piece==null){
        console.log("++++> null cpp")
        return null
    }
    // let stock = await get_stock(item_supplier_obj)
    // if (stock==null){
    //     console.log("++++> null stock")
    //     return null
    // }
    let moq = supply_detail.minimum_order_qty
    if (moq==null){
        console.log("++++> null moq")
        return null
    }
    let destination = order.factory
    let markup = '\
    <tr class="data-row" data-suppliere_row_item="'+item.name+'"  data-destination="'+destination+'">\
        <td class="select-box-supply-product"><input class="supply-order-checkbox supply-section" type="checkbox"/></td>\
        <td class="destination-supply-product">'+order.factory_name+'</td>\
        <td class="product-supply-product">'+item.item_name+'</td>\
        <td class="nop-supply-product">'+total_order_count+'</td>\
        <td class="cpp-supply-product">'+consumption_per_piece+'</td>\
        <td class="tc-supply-product">'+Number(consumption_per_piece)*Number(total_order_count)+'</td>\
        <td class="sm-supply-product" ><span class="background-ash numeric-editable" contenteditable="true">5</span></td>\
        <td class="to-supply-product">'+(Number(consumption_per_piece)*Number(total_order_count)*1.05).toFixed(2)+'</td>\
        <td class="moq-supply-product">'+moq+'</td>\
        <td class="order-supply-prodcut" ><span class="background-ash" contenteditable="true"> </span></td>\
        <td class="sad-supply-product">0</td>\
        <td class="if-supply-product" ><span class="background-ash" contenteditable="true"> </span></td>\
        <td class="reminder-supply-product"><div class="reminder-link" onclick="open_reminder_modal(\''+destination+'\',\''+supply_detail.name+'\')">Reminder</div></td>\
    </tr>'
    if (!SUPPLY_CONTENT[supply_detail.name].hasOwnProperty(destination)){
        SUPPLY_CONTENT[supply_detail.name][destination] = {"items":[item.name],"count":1}
        tbody_element.append(markup)
        tbody_element.children(".data-row[data-destination|='"+destination+"']").children(".sm-supply-product").children(".numeric-editable").on('input',function(e){
            set_theoritical_order_of_row(tbody_element,$(this),Number(consumption_per_piece)*Number(total_order_count),destination)
        })
    }else{
        SUPPLY_CONTENT[supply_detail.name][destination]["items"].push(item.name)
        SUPPLY_CONTENT[supply_detail.name][destination]["count"] = SUPPLY_CONTENT[supply_detail.name][destination]["count"] + 1
        tbody_element.children(".data-row[data-destination|='"+destination+"']").last().after(markup)
        tbody_element.children(".data-row[data-destination|='"+destination+"']").last().children(".sm-supply-product").children(".numeric-editable").on('input',function(e){
            set_theoritical_order_of_row(tbody_element,$(this),Number(consumption_per_piece)*Number(total_order_count),destination)
        })
        let to = await empty_rows(destination,tbody_element).then()
        if (tbody_element.children(".summary-row[data-destination|='"+destination+"']").length==0){
            add_summary_row(tbody_element,destination,0,moq,to,supply_detail)
        }else{
            tbody_element.children(".data-row[data-destination|='"+destination+"']").last().children(".sm-supply-product").children(".numeric-editable").trigger("input")
        }
    }
}
async function empty_rows(destination,tbody_element){
    let to = 0
    tbody_element.children(".data-row[data-destination|='"+destination+"']").each(function(){
        $(this).children(".order-supply-prodcut").empty()
        $(this).children(".reminder-supply-product").empty() 
        $(this).children(".if-supply-product").empty()        
        $(this).children(".select-box-supply-product").empty() 
        to = to + Number($(this).children(".to-supply-product").text())
    })
    return to
}

function add_summary_row(tbody_element,destination,stock,moq,to,supply_detail){

    let markup = '\
    <tr class="summary-row"  data-destination="'+destination+'">\
        <td class="select-box-supply-product"><input  class="supply-order-checkbox supply-section" type="checkbox"/></td>\
        <td class="destination-supply-product"></td>\
        <td class="product-supply-product"></td>\
        <td class="nop-supply-product"></td>\
        <td class="cpp-supply-product"></td>\
        <td class="tc-supply-product"></td>\
        <td class="sm-supply-product" ></td>\
        <td class="to-supply-product">'+to.toFixed(2)+'</td>\
        <td class="moq-supply-product">'+moq+'</td>\
        <td class="order-supply-prodcut" ><span class="background-ash" contenteditable="true"> </span></td>\
        <td class="sad-supply-product">'+stock+'</td>\
        <td class="if-supply-product" ><span class="background-ash" contenteditable="true"> </span></td>\
        <td class="reminder-supply-product"><div class="reminder-link" onclick="open_reminder_modal(\''+destination+'\',\''+supply_detail.name+'\')">Reminder</div></td>\
    </tr>'
    tbody_element.children(".data-row[data-destination|='"+destination+"']").last().after(markup)
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

function set_theoritical_order_of_row(tbody_element,this_element,total_consumption,destination){
    let rate = Number(this_element.text())
    this_element.parent().parent().children(".to-supply-product").text(((rate+100)/100*total_consumption).toFixed(2))
    let to = 0
    tbody_element.children(".data-row[data-destination|='"+destination+"']").each(function(){
        to = to + Number($(this).children(".to-supply-product").text())
    })
    tbody_element.children(".summary-row[data-destination|='"+destination+"' ]").children(".to-supply-product").text(to.toFixed(2))
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
    '<button  onclick="validate_product_and_supply()" type="button" class="btn btn-light" style="display: inline-block;">Validate produc and supply</button>\
    <button  onclick="validate_product_only()" type="button" class="btn btn-light" style="display: inline-block;">Validate product only</button>')
}

function response_message(title, message, color) {
    frappe.msgprint({
        title: __(title),
        indicator: color,
        message: __(message)
    });
}