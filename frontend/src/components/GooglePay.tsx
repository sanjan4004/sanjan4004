import { useEffect } from "react";
import { Button, Alert } from "react-native";
import { GooglePay } from "@stripe/stripe-react-native";

const GooglePayButton: React.FC = () => {
    useEffect(() => {
        GooglePay.init({
            environment: "Test", // Change to "Production" when live
            merchantName: "WorldTtance",
            countryCode: "US",
            existingPaymentMethodRequired: false,
        }).catch((error) => {
            console.error("Google Pay Initialization Error:", error);
        });
    }, []);

    const handlePayment = async () => {
        try {
            const { token } = await GooglePay.requestPayment({
                totalPrice: "70000",
                currencyCode: "USD",
            });

            const response = await fetch("https://worldttance.com/WorldTtance/api/flutterwave/initiate-payment", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    tx_ref: "WT_324",
                    amount: 70000,
                    currency: "USD",
                    payment_options: "Google Pay",
                    customer: { email: "salimsananwarid@outlook.com", name: "salim namai" },
                    redirect_url: "https://worldttance.com/WorldTtance/api/flutterwave/payment_callback",
                    google_pay_token: token,
                }),
            });

            if (!response.ok) {
                throw new Error("Payment initiation failed");
            }

            Alert.alert("Success", "Payment initiated successfully!");
        } catch (error) {
            Alert.alert("Google Pay Error", error instanceof Error ? error.message : "Unknown error occurred");
        }
    };

    return <Button title="Pay with Google Pay" onPress={handlePayment} />;
};

export default GooglePayButton;
