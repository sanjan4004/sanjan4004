export const validatePaymentDetails = (paymentMethod, details) => {
    const requiredFields = {
        "MobileMoney": ["phone_number", "country"],
        "Card": ["card_number", "cvv", "expiry_date", "cardholder_name"],
        "Bank Transfer": ["bank_name", "account_number"],
        "Binance": ["crypto_type", "crypto_wallet"],
        "USSD": ["phone_number", "bank_name"],
        // Add more payment methods as needed
    };

    const missingFields = requiredFields[paymentMethod]?.filter(field => !details[field]);
    if (missingFields && missingFields.length > 0) {
        throw new Error(`Missing required fields: ${missingFields.join(", ")}`);
    }
};
