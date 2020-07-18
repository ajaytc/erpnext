function add_row(){
    let row_num = parseInt($(".table-body").attr("data-row_count"))+1
    let markup_rows = "<tr id='tablerow-"+row_num.toString()+"'><td><input id='check-"+row_num.toString()+"' type='checkbox'/></td><td><div></div></td><td><div></div></td><td><div></div></td><td class='dropdown'><a class='caret dropdown-toggle' data-toggle='dropdown'></a><ul class='dropdown-menu'><li><button  onclick='delete_row("+row_num.toString()+")' type='button' class='btn btn-light' style='display: inline-block;'>Delete Row</button></li></ul></td></tr>"
    $(".table-body").append(markup_rows);
    $(".table-body").attr("data-row_count",row_num.toString());
}

function delete_row(row_num){
    $("#tablerow-"+row_num.toString()).remove();
}

function add_option(){
    let option_num = parseInt($(".option-block").attr("data-option_count"))+1;
    let markup_options = '<div class="col-4"><div class="row option-inputs"><div class="col-9"><label >{{_("Option '+option_num.toString()+'")}}</label><input  type="text" class="form-control mt-2 option-option"></div><div class="col-2 price-block"><label >{{_("Price")}}</label><input type="text" class="form-control mt-2 option-price"></div></div></div>'
    $("#options").append(markup_options);
    $(".option-block").attr("data-option_count",option_num.toString())
}