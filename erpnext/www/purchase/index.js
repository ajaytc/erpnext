function select_all_chekbox(item) {
    if ($('.select-all-sales-orders-'+item).is(':checked')) {
        $('.sales-order-checkbox-'+item).prop('checked', true);
    } else {
        $('.sales-order-checkbox-'+item).prop('checked', false);
    }
}

function set_sum(itm_code,size){
    var sum = 0
    $("."+itm_code+"-"+size).each(function() {
        sum = sum + Number($( this ).text());
    });
    $("."+itm_code+"-"+size+"-sum").text(sum)
}

function ss(){
    console.log(123)
}