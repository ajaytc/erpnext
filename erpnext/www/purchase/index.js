function select_all_chekbox(item) {
    if ($(this).is(':checked')) {
        $('.sales-order-checkbox-'+item).prop('checked', true);
    } else {
        $('.sales-order-checkbox-'+item).prop('checked', false);
    }
}