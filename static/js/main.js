console.log("JavaScript is working!");

// Example: Fetch data from Django API
fetch("/WorldTtance/api/flutterwave/initiate-payment/", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        recipient: "123",
        amount: "100.00",
        payment_method: "visa"
    })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error("Error:", error));
