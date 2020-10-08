// A reference to Stripe.js initialized with your real test publishable API key.


// The items the customer wants to buy
var stripe = ''
$(function () {
  stripe = Stripe("pk_test_51HPL2BGjxNLAb2efrsMrfkkv9IHc1fJen0khnTPiuA8ES3wHZJrSrDLOFxMHZzRAVsxZaxwR07WCf1tTG1Fny0JD00tafSKSpW");
  makeDom()
});

var purchase = {
  items: [{ id: "xl-tshirt" }]
};

// Disable the button until we have Stripe set up on the page
document.querySelector("button").disabled = true;


function makeStripeIntent() {
  frappe.call({
    method: 'erpnext.modehero.payment_plan.create_payment',
    args: {
      data: {
        plan_name: '{{plan.name}}',
        plan_period: '{{plan_period}}'
      }
    },
    callback: function (r) {
      if (!r.exc) {
        payWithCard(stripe, card, r.message.clientSecret);

      } else {
        console.log(r)
      }
    }
  })
}

function subscriptionComplete() {
  frappe.call({
    method: 'erpnext.modehero.payment_plan.completeSubscription',
    args: {
      data: {
        plan_name: '{{plan.name}}',
        plan_period: '{{plan_period}}'
      }
    },
    callback: function (r) {
      if (!r.exc) {
        frappe.msgprint({
          title: __('Notification'),
          indicator: 'green',
          message: __('Payment Completed Successfully')
      });

      } else {
        console.log(r)
      }
    }
  })
}

var card = '';

function makeDom() {
  var elements = stripe.elements();

  var style = {

    base: {

      color: "#32325d",

      fontFamily: 'Arial, sans-serif',

      fontSmoothing: "antialiased",

      fontSize: "16px",

      "::placeholder": {

      }

    },

    invalid: {

      fontFamily: 'Arial, sans-serif',

      color: "#fa755a",

    }

  };

  card = elements.create("card", { style: style });

  // Stripe injects an iframe into the DOM

  card.mount("#card-element");

  card.on("change", function (event) {

    // Disable the Pay button if there are no card details in the Element

    document.querySelector("button").disabled = event.empty;

    document.querySelector("#card-error").textContent = event.error ? event.error.message : "";

  });


}

$('#submit').click(function (event) {
  event.preventDefault();
  makeStripeIntent()

})



// Calls stripe.confirmCardPayment

// If the card requires authentication Stripe shows a pop-up modal to

// prompt the user to enter authentication details without leaving your page.

var payWithCard = function (stripe, card, clientSecret) {

  loading(true);

  stripe

    .confirmCardPayment(clientSecret, {

      payment_method: {

        card: card

      }

    })

    .then(function (result) {

      if (result.error) {

        // Show error to your customer

        showError(result.error.message);

      } else {

        // The payment succeeded!

        orderComplete(result.paymentIntent.id);

      }

    });

};



/* ------- UI helpers ------- */

// Shows a success message when the payment is complete

var orderComplete = function (paymentIntentId) {

  loading(false);


  document.querySelector(".result-message").classList.remove("hidden");

  document.querySelector("button").disabled = true;
  subscriptionComplete()
  makeDom()


};

// Show the customer the error from Stripe if their card fails to charge

var showError = function (errorMsgText) {

  loading(false);

  var errorMsg = document.querySelector("#card-error");

  errorMsg.textContent = errorMsgText;

  setTimeout(function () {

    errorMsg.textContent = "";

  }, 4000);

};

// Show a spinner on payment submission

var loading = function (isLoading) {

  if (isLoading) {

    // Disable the button and show a spinner

    document.querySelector("button").disabled = true;

    document.querySelector("#spinner").classList.remove("hidden");

    document.querySelector("#button-text").classList.add("hidden");

  } else {

    document.querySelector("button").disabled = false;

    document.querySelector("#spinner").classList.add("hidden");

    document.querySelector("#button-text").classList.remove("hidden");

  }

};



$('#testdisable').click(function () {
  frappe.call({
    method: 'erpnext.modehero.user.auto_deactivate_brands',
    callback: function (r) {
        if (!r.exc) {
            

        } else {
            console.log(r)
        }
    }
})
})