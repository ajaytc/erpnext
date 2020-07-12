window.onload = function(){
    $('.sum-quantity').each(function(){
        let item = $(this).attr('data-item');
        let size = $(this).attr('data-size');
        let sum = get_sum(item,size);
        $(this).text(sum);
    });
}

function get_sum(itm_code,size){
    let sum = 0
    $("."+itm_code+"-"+size).each(function() {
        sum = sum + Number($( this ).attr('data-current_qty'));
    });
    return sum
}