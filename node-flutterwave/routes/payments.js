import express from "express";
import axios from "axios";
import dotenv from "dotenv";
import { sendPaymentConfirmation } from "../services/webhookHandler"; // Ensure correct import path for sendPaymentConfirmation

dotenv.config();

const paymentRoutes = express.Router();

// Function to detect card type based on the starting number
const detectCardType = (cardNumber) => {
    const patterns = {
        Visa: /^4[0-9]{12}(?:[0-9]{3})?$/,
        MasterCard: /^5[1-5][0-9]{14}$/,
        Amex: /^3[47][0-9]{13}$/,
        Discover: /^6(?:011|5[0-9]{2})[0-9]{12}$/,
        JCB: /^(?:2131|1800|35\d{3})\d{11}$/
    };
    for (const [cardType, regex] of Object.entries(patterns)) {
        if (regex.test(cardNumber)) {
            return cardType;
        }
    }
    return "Unknown";
};

// Handler functions for each payment method
const handleMobilePayment = (phone_number, country) => {
    if (!phone_number || !country) {
        throw new Error("Phone number and country are required for mobile payments");
    }
    return { payment_type: "mobilemoney", phone_number, country };
};

const handleCardPayment = (card_number, cvv, expiry_date, cardholder_name) => {
    if (!card_number || !cvv || !expiry_date || !cardholder_name) {
        throw new Error("Card details are required for card payments");
    }
    const cardType = detectCardType(card_number);
    return { payment_type: "card", meta: { card_number, cvv, expiry_date, cardholder_name, cardType } };
};

const handleBankTransferPayment = (bank_name, account_number) => {
    if (!bank_name || !account_number) {
        throw new Error("Bank name and account number are required for Bank Transfer");
    }
    return { payment_type: "banktransfer", meta: { bank_name, account_number } };
};

const handleCryptoPayment = (crypto_type, crypto_wallet) => {
    if (!crypto_type && !crypto_wallet) {
        throw new Error("Crypto type (BTC, ETH, USDT) or wallet address is required");
    }
    return { payment_type: "crypto", meta: { crypto_type, crypto_wallet } };
};

const handleTokenPayment = (token) => {
    if (!token) {
        throw new Error("Payment token is required for Google Pay / Apple Pay");
    }
    return { payment_type: "card", meta: { tokenization: "true", token } };
};

const handleUSSDPayment = (phone_number, bank_name) => {
    if (!phone_number || !bank_name) {
        throw new Error("Phone number and bank name are required for USSD payments");
    }
    return { payment_type: "ussd", meta: { phone_number, bank_name } };
};

// Route to initiate payment
paymentRoutes.post("/WorldTtance/api/flutterwave/initiate-payment", async (req, res) => {
    try {
        const { recipient, amount, currency, payment_method, country, phone_number, token, card_number, cvv, expiry_date, cardholder_name, bank_name, account_number, crypto_type, crypto_wallet } = req.body;

        // Validate required fields
        if (!recipient || !amount || !currency || !payment_method) {
            return res.status(400).json({ error: "Missing required payment fields" });
        }

        let paymentPayload = {
            tx_ref: `WTX-${Date.now()}`,
            amount,
            currency,
            redirect_url: process.env.FLW_REDIRECT_URL,
            customer: { email: "user@example.com" },
            payment_options: "Card, mobilemoney, Bank Transfer, ussd, M-Pesa, Google Pay, Apple Pay, Cryptocurrency",
        };

        // Payment method handlers mapping
        const paymentHandlers = {
            "M-Pesa": handleMobilePayment,   // Adding M-Pesa handler
            "Mobile Wallet": handleMobilePayment,
            "Google Pay": handleTokenPayment,
            "Apple Pay": handleTokenPayment,
            "Card": handleCardPayment,
            "Visa": handleCardPayment,
            "MasterCard": handleCardPayment,
            "Amex": handleCardPayment,
            "Discover": handleCardPayment,
            "Bank Transfer": handleBankTransferPayment,
            "Binance": handleCryptoPayment,
            "Cryptocurrency": handleCryptoPayment,
            "USSD": handleUSSDPayment,
        };

        // Get the handler function for the payment method
        const paymentMethodHandler = paymentHandlers[payment_method];
        
        if (!paymentMethodHandler) {
            return res.status(400).json({ error: "Unsupported payment method" });
        }

        // Call the handler function to generate the payment payload
        const paymentDetails = paymentMethodHandler(phone_number, country, token, card_number, cvv, expiry_date, cardholder_name, bank_name, account_number, crypto_type, crypto_wallet);

        // Merge the handler results into the payment payload
        Object.assign(paymentPayload, paymentDetails);

        console.log("Sending Payment Request:", JSON.stringify(paymentPayload, null, 2));

        // Send payment request to Flutterwave API
        const response = await axios.post("https://api.flutterwave.com/v3/payments", paymentPayload, {
            headers: { Authorization: `Bearer ${process.env.FLW_SECRET_KEY}` },
        });

        const responseData = response.data;
        console.log("Flutterwave API Response:", responseData);

        // Return payment link if successful
        if (responseData.status === "success") {
            return res.json({ payment_link: responseData.data.link });
        } else {
            return res.status(400).json({ error: "Payment initiation failed" });
        }
    } catch (error) {
        console.error("Payment Initiation Error:", error.response ? error.response.data : error.message);
        return res.status(500).json({ error: "Internal server error" });
    }
});

// Webhook Route for Payment Confirmation
paymentRoutes.post("/webhook/send-payment-confirmation", async (req, res) => {  // Corrected the route here
    try {
        const flutterwaveSignature = req.headers["verif-hash"];
        if (!flutterwaveSignature || flutterwaveSignature !== process.env.FLW_SECRET_HASH) {
            console.warn("🚨 Invalid Webhook Signature");
            return res.status(401).json({ error: "Unauthorized webhook access" });
        }

        const event = req.body;
        console.log("🔔 Webhook Event Received:", JSON.stringify(event, null, 2));

        if (event.event === "charge.completed" && event.data.status === "successful") {
            console.log(`💰 Payment Successful for Transaction Ref: ${event.data.tx_ref}`);

            // Forward payment confirmation to Django
            const djangoData = {
                tx_ref: event.data.tx_ref,
                status: event.data.status,
                amount: event.data.amount,
                currency: event.data.currency,
                customer_email: event.data.customer.email || "unknown",
            };

            console.log("Forwarding Payment Confirmation to Django:", djangoData);

            try {
                const djangoResponse = await sendPaymentConfirmation(djangoData);  // Call imported function
                console.log("Django API Response:", djangoResponse);
            } catch (error) {
                console.error("Error sending payment confirmation to Django:", error.response ? error.response.data : error.message);
            }
        } else {
            console.warn(`Payment Failed or Incomplete for Transaction Ref: ${event.data.tx_ref}`);
        }

        res.status(200).json({ message: "Webhook received successfully" });
    } catch (error) {
        console.error("Webhook Processing Error:", error.message);
        res.status(500).json({ error: "Internal server error" });
    }
});

// Test Payment Status Endpoint
paymentRoutes.get("/status", (req, res) => {
    res.json({ message: "Payment status endpoint" });
});

export default paymentRoutes;
