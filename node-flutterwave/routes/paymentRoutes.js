import express from "express";
import { sendPaymentConfirmation } from "../services/webhookHandler"; 
import paymentRoutes from "./payments.js"; // Import the payments.js route

const router = express.Router();

// Route for confirming payments
router.post("/confirm-payment", async (req, res) => {
    try {
        const { transactionRef, status, provider, transactionId } = req.body;

        if (!transactionRef || !status || !provider || !transactionId) {
            return res.status(400).json({ error: "Missing required fields" });
        }

        await sendPaymentConfirmation(transactionRef, status, provider, transactionId);

        res.json({ message: "Payment confirmation sent successfully" });
    } catch (error) {
        console.error("Error confirming payment:", error);
        res.status(500).json({ error: "Internal server error" });
    }
});

// Use the imported payments.js routes
router.use("/payments", paymentRoutes);

export default router;
