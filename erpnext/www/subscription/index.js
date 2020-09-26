

$('.annualPay').click(function () {
  plan_name=$(this).attr('data-name')
  window.location.href = "/payment?name="+plan_name+"&period=Annually";
    
})

$('.monthPay').click(function () {
  plan_name=$(this).attr('data-name')
  window.location.href = "/payment?name="+plan_name+"&period=Monthly";
    
})

