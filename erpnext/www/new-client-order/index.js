$('#addtable').click(() => {
    $('#box1').clone().appendTo('#container')
})

$('.close').click(e => console.log($(e.target).parent()))