window.onload = function(){
    $(".client-modal-link").css("color","#3B3DBF");
    $('.sum-quantity').each(function(){
        let item = $(this).attr('data-item');
        let size = $(this).attr('data-size');
        let prod_order = $(this).attr("data-prod_order");
        let sum = get_sum(item,size,prod_order);
        $(this).text(sum);
    });
    $('.total-sum').each(function(){
        let item = $(this).attr('data-item');
        let prod_order = $(this).attr("data-prod_order");
        let total_sum = get_total_sum(item,prod_order);
        $(this).text("Total : "+total_sum.toString());
    });
}

function get_sum(itm_code,size,prod_order){
    let sum = 0;
    $(".qnty-content-class[data-item_code|='"+itm_code+"'][data-size|='"+size+"'][data-prod_order|='"+prod_order+"']").each(function() {
        sum = sum + Number($( this ).attr('data-current_qty'));
    });
    return sum
}

function get_total_sum(itm_code,prod_order){
    let sum = 0;
    $(".sum-quantity[data-item|='"+itm_code+"'][data-prod_order|='"+prod_order+"']").each(function() {
        sum = sum + Number($( this ).text());
    });
    return sum
}

$(".client-modal-link").click(function(){
    let data_array = ["country","city","phone","email","cusname"];
    for (let k=0;k<data_array.length;k++){
        $("#modal-"+data_array[k]).text($(this).attr("data-"+data_array[k]));
    }
    $("#client-modal").modal('show');
});