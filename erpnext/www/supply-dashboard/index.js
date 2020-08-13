$(document).ready(function () {
    $('.delete').click((e) => {
        console.log($(e.target).parent().parent())
    })
    $('.item').css('cursor', 'pointer')
    $('.item').click(function () {
        let ref = $(this).data('ref')
        {% if isFabric %}
        let prefix = '/fabric-summary'
        {% elif isTrimming %}
        let prefix = '/trimming-summary'
        {% elif isPackaging %}
        let prefix = '/packaging-summary'
        {% endif %}

        window.location.href = `${prefix}?order=${ref}`
    })

    checked=$('.selectedCancelOrder').is(':checked'); 
    if(checked){
        $('#canceled').prop('disabled', false)
    }else{
        $('#canceled').prop('disabled', true)
    }
})
{%if isSupplier%}
var s=0
{%else%}
var s=-1
{%endif%}

$('.sortCol').click(function () {
    col=$(this).data('ref')+s
    tableId=$(this).closest("table").attr('id')
    sortTable(col,tableId)
})

function sortTable(col,tableId) {

    var table, rows, switching, i, x, y, shouldSwitch, mode, switchcount = 0;
    table = document.getElementById(tableId);
    switching = true;
    //Set the sorting direction to ascending:
    mode = "creation";
    /*Make a loop that will continue until
    no switching has been done:*/
    while (switching) {
        //start by saying: no switching is done:
        switching = false;
        rows = table.rows;
        /*Loop through all table rows (except the
        first, which contains table headers):*/
        strng=rows[0].getElementsByTagName("TH")[col].innerHTML.toLowerCase();
        if(strng.includes("date")){
            typ='date'
        }else{
            typ='str'
        }

        for (i = 1; i < (rows.length - 1); i++) {
            //start by saying there should be no switching:
            shouldSwitch = false;
            /*Get the two elements you want to compare,
            one from current row and one from the next:*/
            x = rows[i].getElementsByTagName("TD");
            y = rows[i + 1].getElementsByTagName("TD");
            /*check if the two rows should switch place,
            based on the direction, asc or desc:*/
            if (mode == "creation") {
                if(typ=='date'){
                    d1=x[col].innerHTML.toLowerCase().split(/\//)
                    d2=y[col].innerHTML.toLowerCase().split(/\//)
                    formattedD1=[ d1[1], d1[0], d1[2] ].join('/');
                    formattedD2= [ d2[1], d2[0], d2[2] ].join('/');

                    if (Date.parse(formattedD1) < Date.parse(formattedD2)) {
                        //if so, mark as a switch and break the loop:
                        shouldSwitch = true;
                        break;
                    }
                }else{
                    if (x[col].innerHTML.toLowerCase() > y[col].innerHTML.toLowerCase()) {
                        //if so, mark as a switch and break the loop:
                        shouldSwitch = true;
                        break;
                    }
                }
                
            } else if (mode == "groupType") {
                if (x[0].innerHTML > y[0].innerHTML) {
                    //if so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            /*If a switch has been marked, make the switch
            and mark that a switch has been done:*/
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            //Each time a switch is done, increase this count by 1:
            switchcount++;
        } else {
            /*If no switching has been done AND the direction is "asc",
            set the direction to "desc" and run the while loop again.*/
            if (switchcount == 0 && mode == "creation") {
                mode = "groupType";
                switching = true;
            }
        }
    }
}


$('.selectedCancelOrder').change(function () {
    // $('#delivered').prop('disabled', false)
    checked=$('.selectedCancelOrder').is(':checked'); 
    if(checked){
        $('#canceled').prop('disabled', false)
    }else{
        $('#canceled').prop('disabled', true)
    }
})

$('#canceled').click(function () {
    let selectednames = []

    $('input[name="orderCheck"]:checked').each(function () {
        selectednames.push($(this).attr('data-name'))
    });
    console.log(selectednames)

    if (selectednames.length != 0) {
        frappe.call({
            method: 'erpnext.modehero.supplier.cancelSupplyOrder',
            args: {
                data: {
                    orders: selectednames,
                    orderGroup:"{{orderType}}"
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