$("#product-category-select").change(function(){
    let category =  $('#product-category-select option:selected').val();
    if (!category){
        return null
    }
    $("#product-select").find("option").remove();
    frappe.call({
        method: 'erpnext.modehero.product.get_priducts_of_category',
        args: {
            category:category
        },
        callback: function (r) {
            if (!r.message) {
                return null
            }
            let objects=r.message
            if (objects.length>0){
                for (i = 0; i < objects.length; i++) {
                    let temp_markup = '<option  value="'+objects[i].name+'">'+objects[i].item_name+'</option>';
                    $("#product-select").append(temp_markup);
                }
            }
            else{
                let temp_markup = '<option  value="" disabled selected>No Product Available</option>';
                $("#product-select").append(temp_markup);
            }
        }
    });
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
});

function add_row(){
    let row_num = parseInt($(".table-body").attr("data-row_count"))+1
    let markup_rows = "<tr id='tablerow-"+row_num.toString()+"'><td><input class='checkbox-table-row' data-row_num='"+row_num.toString()+"' type='checkbox'/></td><td><div contenteditable='true' class='from editable table-input-"+row_num.toString()+"'></div></td><td><div contenteditable='true' class='to editable table-input-"+row_num.toString()+"'></div></td><td><div contenteditable='true' class='price editable table-input-"+row_num.toString()+"'></div></td><td class='dropdown'><a class='caret dropdown-toggle' data-toggle='dropdown'></a><ul class='dropdown-menu'><li><button  onclick='delete_row("+row_num.toString()+")' type='button' class='btn btn-light' style='display: inline-block;'>Delete Row</button></li></ul></td></tr>"
    $(".table-body").append(markup_rows);
    $(".table-body").attr("data-row_count",row_num.toString());
    $(".table-input-"+row_num.toString()).keypress(function(e) {
        if (isNaN(String.fromCharCode(e.which))) e.preventDefault();
    });
}

function delete_row(row_num){
    $("#tablerow-"+row_num.toString()).remove();
}

function add_option(){
    console.log($(".price"))
    let option_num = parseInt($(".option-block").attr("data-option_count"))+1;
    let markup_options = '<div class="col-4"><div class="row option-inputs"><div class="col-9"><label >{{_("Option '+option_num.toString()+'")}}</label><input  type="text" class="form-control mt-2 option-option"></div><div class="col-2 price-block"><label >{{_("Price")}}</label><input id="option'+option_num.toString()+'-price" type="text" class="form-control mt-2 option-price"></div></div></div>'
    $("#options").append(markup_options);
    $(".option-block").attr("data-option_count",option_num.toString());
    $("#option"+option_num.toString()+"-price").keypress(function(e) {
        if (isNaN(String.fromCharCode(e.which))) e.preventDefault();
    });
}