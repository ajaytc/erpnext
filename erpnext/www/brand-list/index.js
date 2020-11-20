$("#download-button").click(function(){
    frappe.call({
        method: 'erpnext.modehero.bo.get_excel_of_brands',
        args:{

        },
        callback: function (r) {
            if (r) {
                if (r.message['status'] == "ok") {
                    downloadEXCEL(r.message.stream)
                    return null
                }
                response_message('Unsuccessfull', 'Excel file geeration unsuccessfull!', 'red');
                return null;
            }
            response_message('Unsuccessfull', 'Excel file geeration unsuccessfull!', 'red');
        }
    });
})


function downloadEXCEL(csvStr) {
    let hiddenElement = document.createElement('a');
    hiddenElement.href = 'data:text/csv;charset=utf-8,' + encodeURI(csvStr);
    hiddenElement.target = '_blank';
    hiddenElement.download = 'output.csv';
    hiddenElement.click();
}

function response_message(title, message, color) {
    frappe.msgprint({
        title: __(title),
        indicator: color,
        message: __(message)
    });
}

