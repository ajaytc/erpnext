$('.product').click(function () {
    product_name = $(this).parent().attr('data-product')
    // location.href('/product?'+product_name)
    window.location.href = "/product?name="+product_name;

})


$('.deleteSelection').change(function () {
    // $('#delivered').prop('disabled', false)
    checked=$('.deleteSelection').is(':checked'); 
    if(checked){
        $('#deleteBtn').prop('disabled', false)
    }else{
        $('#deleteBtn').prop('disabled', true)
    }
})


$('#deleteBtn').click(function () {
    let selectednames = []

    $('input[name="productChecked"]:checked').each(function () {
        selectednames.push($(this).parent().parent().parent().attr('data-product'))
    });
    console.log(selectednames)

    if (selectednames.length != 0) {
        frappe.call({
            method: 'erpnext.modehero.product.deleteProduct',
            args: {
                data: {
                    products: selectednames
                }
            },
            callback: function (r) {
                if (!r.exc) {
                    console.log(r)
                    location.reload();

                } else {
                    console.log(r)
                }
            }
        })
    } else {
        console.error('Order not selected')

    }


})