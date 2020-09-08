$(document).ready(function () {
    $('.delete').click((e) => {
        console.log($(e.target).parent().parent())
    })
})

var stock_name =null;
var price = null;
var in_stock = null;
var fabric_name = null;
var old_stock =null;
var unit_price =null;

$('#updateStock').on('show.bs.modal', function (event) {

    stock_name = $('.selectedfabric:checked').attr('data-name')
    in_stock = $('.selectedfabric:checked').attr('data-stock')
    old_stock = $('.selectedfabric:checked').attr('data-stock')
    fabric_name = $('.selectedfabric:checked').attr('data-item')
    unit_price = $('.selectedfabric:checked').attr('data-price')

    var modal = $(this)

    modal.find('.modal-title').text('Update Stock of ' + fabric_name)
    modal.find('.modal-body #in-stock').val(old_stock)
    modal.find('.modal-body #real-stock').val(in_stock)

})

$('#validatebutton').click(() => {
    in_stock = $('.modal-body #real-stock').val()

    console.log("Old Stock:"+old_stock)
    console.log("New Stock:"+in_stock)

    frappe.call({
        method: 'erpnext.modehero.stock.updateStock',
        args: {
            stock_name,
            quantity : in_stock,
            old_quantity : old_stock,
            description : 'Update Stock',
            price : unit_price
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
                window.location.reload()
            }
        }
    })

})

$('#directShip').on('show.bs.modal', function (event) {
    stock_name = $('.selectedfabric:checked').attr('data-name')
    in_stock = $('.selectedfabric:checked').attr('data-stock')
    old_stock = $('.selectedfabric:checked').attr('data-stock')
    fabric_name = $('.selectedfabric:checked').attr('data-item')
    unit_price = $('.selectedfabric:checked').attr('data-price')

    var modal = $(this)

    modal.find('.modal-title').text('Direct Ship ' + fabric_name)
})

$('#shipbutton').click(() => {
    var amount = $('.modal-body #quantity').val()
    var destination = $('.modal-body #destination').val()
    
    console.log(amount)
    console.log(destination)

    frappe.call({
        method: 'erpnext.modehero.stock.directShip',
        args: {
            stock_name,
            amount,
            old_stock,
            description : destination,
            price : unit_price,
            order_type:'directship-fabric'
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
                window.location.reload()
            }
        }
    })
    console.log(amount+ " of "+ fabric_name+ " shipped to " + destination)
})


$('#shipFromExisting').on('show.bs.modal', function (event) {

    var modal = $(this)

    var vendor = $('.modal-body #selected-vendor').val()
    console.log(vendor)

    $('.selected-vendor').click(vendorUpdateCallback)

    $('.selected-orders').click(purchaseUpdateCallback)
    
})

function generateOptions(values) {
    let html = ''
    values.map(v => {
        html += `<option value="${v.name}">${v.name}</option>`
    })
    return html
}

const vendorUpdateCallback = (e) => {
    var vendor = $(e.target).find("option:selected").val()
    console.log(vendor)
    frappe.call({
        method: 'erpnext.modehero.stock.get_fabric_orders',
        args: {
            vendor
        },
        callback: function (r) {
            //console.log(r.message)
            $('#orders').html(generateOptions(r.message))
        }
    });
}
const purchaseUpdateCallback = (e) => {
    var order = $(e.target).find("option:selected").val()
    console.log(order)

    frappe.call({
        method: 'erpnext.modehero.stock.get_order_details_fabric',
        args: {
            order
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r.message)
                name = r.message.fabric_ref
                qty = r.message.quantity
                stock_name = r.message.stock_name
                old_stock = r.message.old_stock
                unit_price = r.message.price

                console.log(name)
                console.log(qty)
                let inputfield = generateInputField(name,qty)
                console.log(inputfield)
                $('#input-field').html(inputfield)
            }
        }
    });
}

function generateInputField(name,qty) {
    return `    <label>${name}</label>    
                <input type="number" class="form-control" value="${qty}" min="0" max="${qty} id="shipfromexistingqty">
    `
}

$('#shipfromExistingbutton').click(() => {
    var amount = $('.modal-body #shipfromexistingqty').val()
    frappe.call({
        method: 'erpnext.modehero.stock.shipFromExisting',
        args: {
            stock_name,
            amount,
            old_stock,
            description : 'Fabric Received',
            price : unit_price
        },
        callback: function (r) {
            if (!r.exc) {
                console.log(r)
                window.location.reload()
            }
        }
    })
})