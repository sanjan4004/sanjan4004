const express = require("express");
const axios = require("axios");
require("dotenv").config();

const router = express.Router();

// Function to send payment confirmation to Django
async function sendPaymentConfirmation(tx_ref, status, amount, currency, customer_email) {
    try {
        const response = await axios.post(`${process.env.DJANGO_API_URL}/api/update-transaction`, {
            tx_ref,
            status,
            amount,
            currency,
            customer_email
        }, {
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${process.env.DJANGO_API_SECRET_KEY}`
            }
        });

        console.log(" Payment Confirmation Sent to Django:", response.data);
    } catch (error) {
        console.error(" Error sending payment confirmation:", error.response ? error.response.data : error.message);
    }
}

// Webhook Endpoint
router.post("/WorldTtance/api/flutterwave/webhook", async (req, res) => {
    try {
        // Validate webhook signature from Flutterwave
        const receivedSignature = req.headers["verif-hash"];
        if (!receivedSignature || receivedSignature !== process.env.FLW_SECRET_HASH) {
            console.log(" Invalid webhook signature.");
            return res.status(401).json({ error: "Unauthorized webhook access" });
        }

        console.log(" Received Webhook Event:", JSON.stringify(req.body, null, 2));

        // Extract data from webhook payload
        const event = req.body;
        if (!event || !event.data) {
            console.log(" Invalid webhook payload.");
            return res.status(400).json({ error: "Invalid webhook payload" });
        }

        const tx_ref = event.data.tx_ref;
        const status = event.data.status;
        const amount = event.data.amount;
        const currency = event.data.currency;
        const customer_email = event.data.customer?.email || "unknown";

        console.log(` Processing Transaction: ${tx_ref}`);

        // Check if the transaction was successful
        if (status === "successful") {
            console.log(`💰 Payment Successful for Transaction Ref: ${tx_ref}`);

            // 🔹 Calculate transaction fee (4% of amount)
            const fee = (amount * 0.04).toFixed(2);
            const binanceWallet = process.env.BINANCE_WALLET_ADDRESS;

            try {
                // 🔹 Send fee to Binance AdminWallet
                const binanceResponse = await axios.post("https://api.binance.com/sapi/v1/capital/withdraw/apply", {
                    coin: "USDT",
                    amount: fee,
                    address: binanceWallet,
                    network: "BSC"
                }, {
                    headers: {
                        "X-MBX-APIKEY": process.env.BINANCE_API_KEY
                    }
                });

                console.log(" Fee sent to Binance AdminWallet:", binanceResponse.data);
            } catch (error) {
                console.error(" Fee transfer failed:", error.response ? error.response.data : error.message);
            }

            // 🔹 Send payment confirmation to Django
            await sendPaymentConfirmation(tx_ref, status, amount, currency, customer_email);
        } else {
            console.log(` Payment Failed or Incomplete for Transaction Ref: ${tx_ref}`);
        }

        res.status(200).json({ message: "Webhook processed successfully" });

    } catch (error) {
        console.error(" Webhook Processing Error:", error);
        res.status(500).json({ error: "Internal Server Error" });
    }
});

module.exports = router;
