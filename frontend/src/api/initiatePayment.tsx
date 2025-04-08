import axios from "axios";
import { Alert } from "react-native";
import { NavigationProp } from "@react-navigation/native";
import { DJANGO_API_URL } from "@env"; // Load from environment variables

// Define expected response structure
interface PaymentResponse {
    payment_link?: string;
    error?: string;
}

// Define function parameter types
interface InitiatePaymentParams {
    recipient: string;
    amount: number;
    currency: string;
    paymentMethod: string;
    country: string;
    phoneNumber?: string;
    navigation: NavigationProp<any>; // Ensure this is properly typed if possible
}

/**
 * Initiates a payment request to the Django backend and navigates to the payment page.
 */
export const initiatePayment = async ({
    recipient,
    amount,
    currency,
    paymentMethod,
    country,
    phoneNumber,
    navigation,
}: InitiatePaymentParams): Promise<void> => {
    try {
        // Validate input before making the API request
        if (!recipient || !amount || !currency) {
            Alert.alert("Validation Error", "All payment details must be provided.");
            return;
        }

        // Ensure DJANGO_API_URL is available
        if (!DJANGO_API_URL) {
            Alert.alert("Error", "API URL is not configured.");
            return;
        }

        const apiUrl = `${DJANGO_API_URL}/api/flutterwave/initiate-payment`; // Load API URL from env

        // Construct payment data
        const paymentData = {
            recipient,
            amount,
            currency,
            payment_method: paymentMethod,
            country,
            phone_number: ["M-pesa", "Mobilemoney"].includes(paymentMethod.toLowerCase())
                ? phoneNumber
                : null,
        };

        // Include all supported payment methods explicitly for backend compatibility
        const supportedPaymentMethods = [
            "M-pesa",
            "Mobilemoney",
            "Card",
            "Bank Transfer",
            "Cryptocurrency",
            "Google pay",
            "Apple pay",
        ];

        if (!supportedPaymentMethods.includes(paymentMethod.toLowerCase())) {
            Alert.alert("Unsupported Method", `${paymentMethod} is not supported.`);
            return;
        }

        // Make API request
        const response = await axios.post<PaymentResponse>(apiUrl, paymentData, {
            headers: { "Content-Type": "application/json" },
        });

        if (response.status === 200 && response.data.payment_link) {
            console.log("Payment Link:", response.data.payment_link);
            navigation.navigate("FlutterwavePayment", { paymentUrl: response.data.payment_link });
        } else {
            console.error("Payment API Error:", response.data.error);
            Alert.alert("Payment Error", response.data.error || "Something went wrong. Please try again.");
        }
    } catch (error: any) {
        // Improved error handling with more specific messages
        console.error("Payment initiation error:", error.response?.data || error.message);
        const errorMessage =
            error.response?.data?.error || "Failed to initiate payment. Please check your network.";
        Alert.alert("Error", errorMessage);
    }
};
