$( document ).ready(function() {
    $('.segment').each(function (index,value) {
       if($(value).find('.piecesCheck').length == $(value).find('.pieces').length){
           $(value).find('#fullCheck').show()
       }
        
    })
});