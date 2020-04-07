var tablecount = 1;

$('#addtable').click(() => {
    $('#box1').clone().appendTo('#container')
    tablecount++
})

$('.close').click(e => console.log($(e.target).parent()))


$('#validate').click(() => {
    let p1 = $('.selected-product')[0]
    console.log($(p1).find("option:selected").text())
})

$('.selected-product').change((e) => {
    product = $(e.target).find("option:selected").text()
    // frappe.call({
    //     method: 'frappe.client.get_value',
    //     args: {
    //         'doctype': 'Item',
    //         'filters': {'name': item_code},
    //         'fieldname': [
    //             'item_name',
    //             'web_long_description',
    //             'description',
    //             'image',
    //             'thumbnail'
    //         ]
    //     },
    //     callback: function(r) {
    //         if (!r.exc) {
    //             // code snippet
    //         }
    //     }
    // });
})