dataflag=false
displaySizeFlag=false
$('.productName').click(function () {
    // $(this).parent().find('#sizeDetails').show()
    el = $(this)
    itemName = $(this).attr('data-product')
    orderNo = $(this).attr('data-order')

    getSizeDetails(el,itemName,orderNo)
    

    // if(!displaySizeFlag){
    //     getSizeDetails(el,itemName,orderNo)
    // }else{
    //     if(displaySizeFlag){
    //         $(el).parent().find('#sizeDetails').hide()
    //         displaySizeFlag=false
    //     }else{
    //         $(el).parent().find('#sizeDetails').show()
    //         displaySizeFlag=true
    //     }
    // }
    

})


function getSizeDetails(el,item,order) {
    frappe.call({
        method: 'erpnext.modehero.uniform.getSizesDetails',
        args: {
            data: {
                item_name: item,
                order_no: order
            }
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r.message)
                html = ``
                $.each(r.message, function (key, value) {
                    qty = value[1]
                    for (a = 0; a < qty; a++) {
                        html = html + `<tr style='background-color:white'>
                            <td style="background-color: white !important;"><label class="custom-checkbox">
                                <input type="checkbox"  data-name="">
                                <span class="icon"></span>
                            </label></td>
                            <td style="background-color: transparent !important;">1</td>
                            <td style="background-color: transparent !important;">`+ value[4] + `</td>
                            <td style="background-color: transparent !important;">`+ value[5] + `</td>
                        </tr>`
                    }
                })
                $(el).parent().find('#sizeDetailBody').html(html)
                $(el).parent().find('#sizeDetails').toggle('slide', {direction: 'up'}, 1000)
                // $(el).parent().find('#sizeDetails').show()
                // displaySizeFlag=true
                // dataflag=true


            } else {
                console.log(r)
            }
        }
    })
}