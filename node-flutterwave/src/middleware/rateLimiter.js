import rateLimit from 'express-rate-limit';

// Set up a rate limit for the payment route
const paymentLimiter = rateLimit({
    windowMs: 10 * 60 * 1000, // 10 minutes
    max: 5, // Limit to 5 requests per 10 minutes
    message: "Too many payment requests from this IP, please try again later",
});

paymentRoutes.post("/WorldTtance/api/flutterwave/initiate-payment", paymentLimiter, async (req, res) => {
    // Your payment initiation logic here
});
