require("dotenv").config();
const express = require("express");
const Flutterwave = require("flutterwave-node-v3");
const axios = require("axios");
const bodyParser = require("body-parser");
const cors = require("cors");
const crypto = require("crypto");

const app = express();
const PORT = process.env.PORT || 5000;

// Enforce HTTPS
app.use((req, res, next) => {
    if (req.headers["x-forwarded-proto"] !== "https") {
        return res.redirect("https://" + req.headers.host + req.url);
    }
    next();
});

// Initialize Flutterwave with public and secret keys
const flw = new Flutterwave(process.env.FLW_PUBLIC_KEY, process.env.FLW_SECRET_KEY);
const FLUTTERWAVE_SECRET_KEY = process.env.FLW_SECRET_KEY;
const FLUTTERWAVE_SECRET_HASH = process.env.FLW_SECRET_HASH;
const FLW_REDIRECT_URL = process.env.FLW_REDIRECT_URL;

// Ensure environment variables are loaded
console.log("FLW_SECRET_KEY Loaded:", !!FLUTTERWAVE_SECRET_KEY);
console.log("FLW_PUBLIC_KEY Loaded:", !!process.env.FLW_PUBLIC_KEY);

const corsOptions = {
    origin: ["https://worldttance.com"], 
    methods: "GET,HEAD,PUT,PATCH,POST,DELETE",
    credentials: true
};
app.use(cors(corsOptions));
app.use(bodyParser.json());

// 📌 Middleware for logging incoming requests (only in development)
if (process.env.NODE_ENV === "development") {
    app.use((req, res, next) => {
        console.log(`📌 [${req.method}] ${req.url}`);
        console.log("Headers:", req.headers);
        console.log("Body:", JSON.stringify(req.body, null, 2));
        next();
    });
}

// 📌 Process Payment from Django API
app.post("/WorldTtance/api/flutterwave/process-payments", async (req, res) => {
    try {
        const { transaction_id, payment_method, amount, currency, recipient } = req.body;

        const flutterwaveResponse = await axios.post(
            "https://api.flutterwave.com/v3/payments",
            {
                tx_ref: `txn_${transaction_id}`,
                amount,
                currency,
                payment_options: [payment_method],
                redirect_url: FLW_REDIRECT_URL,
                customer: {
                    name: recipient.name,
                    email: recipient.email || "worldttance@gmail.com",
                    phone_number: recipient.wallet || "",
                }
            },
            {
                headers: { Authorization: `Bearer ${FLUTTERWAVE_SECRET_KEY}` }
            }
        );

        res.json(flutterwaveResponse.data);
    } catch (error) {
        console.error("🚨 Flutterwave API Error:", error.response?.data || error.message);
        res.status(500).json({ status: "error", message: "Payment processing failed" });
    }
});

// 📌 Direct API Payment Processing
app.post("/pay", async (req, res) => {
    try {
        console.log("Received Payment Request:", req.body);

        const {
            tx_ref, amount, currency, payment_options,
            customer, redirect_url,
            google_pay_token, apple_pay_token, card_details
        } = req.body;

        if (!customer || !customer.email) {
            return res.status(400).json({ error: "Customer email is required" });
        }

        let paymentData = {
            tx_ref,
            amount,
            currency,
            redirect_url,
            customer: {
                email: customer.email,
                name: customer.name || "Anonymous"
            },
            customizations: {
                title: "WorldTtance Payment",
                description: "Transaction payment",
                logo: "https://worldttance.com/static/images/logo.png"
            }
        };

        let response;

        switch (payment_options.toLowerCase()) {
            case "visa":
            case "mastercard":
            case "americanexpress":
                if (!card_details || !card_details.number || !card_details.cvv || !card_details.expiry_month || !card_details.expiry_year) {
                    return res.status(400).json({ error: "Card details (number, CVV, expiry) are required" });
                }
                response = await flw.Charge.card({
                    ...paymentData,
                    payment_type: "card",
                    card_number: card_details.number,
                    cvv: card_details.cvv,
                    expiry_month: card_details.expiry_month,
                    expiry_year: card_details.expiry_year,
                });
                break;

            case "google pay":
                if (!google_pay_token) {
                    return res.status(400).json({ error: "Google Pay token is required" });
                }
                response = await flw.Charge.tokenized({ ...paymentData, payment_type: "google_pay", token: google_pay_token });
                break;

            case "apple pay":
                if (!apple_pay_token) {
                    return res.status(400).json({ error: "Apple Pay token is required" });
                }
                response = await flw.Charge.tokenized({ ...paymentData, payment_type: "apple_pay", token: apple_pay_token });
                break;

            case "bank transfer":
                if (!customer.bank_code || !customer.account_number) {
                    return res.status(400).json({ error: "Bank code and account number are required" });
                }
                response = await flw.Transfer.initiate({
                    account_bank: customer.bank_code,
                    account_number: customer.account_number,
                    amount,
                    currency,
                    narration: "Bank transfer payment",
                    reference: tx_ref,
                    debit_currency: currency
                });
                break;

            case "m-pesa":
                if (!customer.phone_number || !/^\d+$/.test(customer.phone_number)) {
                    return res.status(400).json({ error: "Valid phone number is required for M-Pesa payments" });
                }
                response = await flw.MobileMoney.mpesa({
                    tx_ref,
                    amount,
                    currency,
                    order_id: `order_${tx_ref}`,
                    ip: req.ip || "127.0.0.1",
                    customer: {
                        email: customer.email,
                        phone_number: customer.phone_number,
                        name: customer.name || "Anonymous"
                    },
                    redirect_url,
                });
                break;

            case "cryptocurrency":
            case "bitcoin":
            case "binance":
                response = await flw.PaymentLink.create({
                    ...paymentData,
                    payment_options: "crypto"
                });

                if (!response || response.status !== "success") {
                    return res.status(400).json({ error: response?.message || "Failed to initiate crypto payment" });
                }
                return res.json({ status: "success", data: response });

            default:
                return res.status(400).json({ error: `Unsupported payment method: ${payment_options}` });
        }

        if (!response || response.status !== "success") {
            return res.status(400).json({ error: response?.message || "Payment failed" });
        }

        res.json({ status: "success", data: response });
    } catch (error) {
        console.error("🚨 Payment Processing Error:", error);
        res.status(500).json({ error: "Internal Server Error" });
    }
});

// Correct Webhook Route for Flutterwave
app.post("/WorldTtance/api/flutterwave/webhook", async (req, res) => {
    try {
        const signature = req.headers["verif-hash"];
        const computedHash = crypto.createHmac("sha256", FLUTTERWAVE_SECRET_HASH)
            .update(JSON.stringify(req.body))
            .digest("hex");

        if (signature !== computedHash) {
            return res.status(400).json({ error: "Invalid signature" });
        }

        console.log("Webhook Received:", req.body);
        const paymentStatus = req.body.data.status;

        if (paymentStatus === "successful") {
            // Handle the successful payment (e.g., mark the transaction as complete in DB)
            console.log("Payment Successful");
        }

        res.status(200).send("Webhook received");
    } catch (error) {
        console.error("🚨 Webhook Error:", error);
        res.status(500).send("Internal Server Error");
    }
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
