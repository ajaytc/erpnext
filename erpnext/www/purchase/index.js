window.onload = function(){
    $('.sum-quantity').each(function(){
        let item = $(this).attr('data-item');
        let size = $(this).attr('data-size');
        let sum = get_sum(item,size);
        $(this).text(sum);
    });
}

function select_all_chekbox(item) {
    if ($('.select-all-sales-orders-'+item).is(':checked')) {
        $('.sales-order-checkbox-'+item).prop('checked', true);
    } else {
        $('.sales-order-checkbox-'+item).prop('checked', false);
    }
}

function get_sum(itm_code,size){
    let sum = 0
    $("."+itm_code+"-"+size).each(function() {
        sum = sum + Number($( this ).text());
    });
    return sum
}
