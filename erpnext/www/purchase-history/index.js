window.onload = function(){
    $('.sum-quantity').each(function(){
        let item = $(this).attr('data-item');
        let size = $(this).attr('data-size');
        let group_no = $(this).attr("data-group_no");
        let sum = get_sum(item,size,group_no);
        $(this).text(sum);
    });
    $('.total-sum').each(function(){
        let item = $(this).attr('data-item');
        let group_no = $(this).attr("data-group_no");
        let total_sum = get_total_sum(item,group_no);
        $(this).text("Total : "+total_sum.toString());
    });
}

function get_sum(itm_code,size,group_no){
    let sum = 0;
    $(".qnty-content-class[data-item_code|='"+itm_code+"'][data-size|='"+size+"'][data-group_no|='"+group_no+"']").each(function() {
        sum = sum + Number($( this ).attr('data-current_qty'));
    });
    return sum
}

function get_total_sum(itm_code,group_no){
    let sum = 0;
    $(".sum-quantity[data-item|='"+itm_code+"'][data-group_no|='"+group_no+"']").each(function() {
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