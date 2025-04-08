require("dotenv").config();
import express, { Request, Response } from "express";
import Flutterwave from "flutterwave-node-v3";
import cors from "cors";
import paymentRoutes from "../routes/paymentRoutes"; // Import payment routes
import webhookHandler from "../services/webhookHandler"; // Import the webhook handler
import https from "https";
import fs from "fs";

// Initialize Express App
const app = express();
const PORT = process.env.PORT || 5000;

// Initialize Flutterwave with Secret Key
const flw = new Flutterwave(process.env.FLUTTERWAVE_SECRET_KEY);

// Middleware
app.use(express.json()); // Parse JSON requests
app.use(cors()); // Enable CORS for frontend access

// Webhook Route (for handling Flutterwave events)
app.use("/WorldTtance/api/flutterwave/webhook", webhookHandler);

// Use the payments route for all API requests starting with "/api/payments"
app.use("/api/payments", paymentRoutes);

// API Endpoint: Initiate Payment with All Payment Methods
app.post("/pay/flutterwave/initiate-payment", async (req: Request, res: Response) => {
    try {
        const { email, name, amount, currency } = req.body;

        // Validate required fields
        if (!email || !name || !amount || !currency) {
            return res.status(400).json({ error: "Missing required fields" });
        }

        // Generate unique transaction reference
        const transactionRef = `WT_${Date.now()}`;

        const payload = {
            tx_ref: transactionRef,
            amount,
            currency,
            redirect_url: process.env.REDIRECT_URL || 
                "https://worldttance.com/WorldTtance/api/flutterwave/payment_callback",
            payment_options: "card, mobilemoney, ussd, banktransfer, barter, googlepay, applepay, cryptocurrency, mpesa",
            customer: { email, name },
            customizations: {
                title: "WorldTtance Payment",
                description: "Secure Transaction",
                logo: "https://worldttance.com/static/logo.png"
            }
        };

        console.log(" Sending Payload to Flutterwave:", payload);

        // Create Payment Link using Flutterwave SDK
        const response = await flw.PaymentLink.create(payload);

        if (response.status === "success") {
            console.log("  Payment Link Created:", response.data.link);
            return res.json({ paymentLink: response.data.link });
        } else {
            console.error("  Flutterwave API Error:", response.message);
            return res.status(500).json({ error: "Failed to create payment link" });
        }
    } catch (error: any) {
        console.error("  Error Initiating Payment:", error.response?.data || error.message);
        return res.status(500).json({ error: "Internal server error" });
    }
});

// HTTPS Server Configuration (Using SSL Certificates)
const httpsOptions = {
    key: fs.readFileSync('./certs/key.pem'),  // Path to your private key file
    cert: fs.readFileSync('./certs/cert.pem') // Path to your certificate file
};

// Start HTTPS Server
https.createServer(httpsOptions, app).listen(PORT, () => {
    console.log(` HTTPS Server running at https://localhost:${PORT}`);
});
