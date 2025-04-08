const axios = require("axios");

async function sendPaymentConfirmation(transactionRef, status, provider, transactionId) {
    try {
        const response = await axios.post(process.env.DJANGO_WEBHOOK_URL, {
            transaction_reference: transactionRef,
            status: status,
            provider: provider,
            transaction_id: transactionId
        });

        console.log("Payment Confirmation Sent:", response.data);
    } catch (error) {
        console.error("Error sending payment confirmation:", error.response ? error.response.data : error.message);
    }
}

module.exports = sendPaymentConfirmation;
