$('#cat_col').click(function () {

    sortTable()
})


function sortTable() {

    var table, rows, switching, i, x, y, shouldSwitch, mode, switchcount = 0;
    table = document.getElementById("allSuppliers");
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
                if (x[0].innerHTML.toLowerCase() > y[0].innerHTML.toLowerCase()) {
                    //if so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            } else if (mode == "groupType") {
                if (x[8].innerHTML > y[8].innerHTML) {
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
