import React, { useEffect } from "react";
import { Button, Alert } from "react-native";
import { useStripe } from "@stripe/stripe-react-native";

const ApplePayButton: React.FC = () => {
    const { presentApplePay, confirmApplePayPayment } = useStripe();

    useEffect(() => {
        const checkApplePayAvailability = async () => {
            try {
                const { error } = await presentApplePay({
                    cartItems: [{ label: "WorldTtance", amount: "70000" }],
                    country: "US",
                    currency: "USD",
                    merchantIdentifier: "merchant.com.worldttance",
                });

                if (error) {
                    Alert.alert("Apple Pay Error", error.message);
                }
            } catch (error) {
                if (error instanceof Error) {
                    Alert.alert("Apple Pay Error", error.message);
                } else {
                    Alert.alert("Apple Pay Error", "An unknown error occurred.");
                }
            }
        };

        checkApplePayAvailability();
    }, []);

    const handleApplePay = async () => {
        try {
            const { paymentIntent, error } = await presentApplePay({
                cartItems: [{ label: "WorldTtance", amount: "70000" }],
                country: "US",
                currency: "USD",
                merchantIdentifier: "merchant.com.WorldTtance",
            });

            if (error) {
                Alert.alert("Apple Pay Error", error.message);
                return;
            }

            if (paymentIntent) {
                const response = await fetch("https://worldttance.com/WorldTtance/api/flutterwave/initiate-payment", { // Updated URL
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        tx_ref: "WT_324",
                        amount: 70000,
                        currency: "USD",
                        payment_options: "Apple Pay",
                        customer: { email: "salimsananwarid@outlook.com", name: "salim namai" },
                        redirect_url: "https://worldttance.com/WorldTtance/api/flutterwave/payment_callback", // Updated URL
                        apple_pay_token: paymentIntent.id, // Send payment intent ID
                    }),
                });

                if (!response.ok) {
                    throw new Error("Failed to initiate payment.");
                }

                Alert.alert("Payment Successful!", "Your Apple Pay transaction was completed.");
            }
        } catch (error) {
            if (error instanceof Error) {
                Alert.alert("Payment Failed", error.message);
            } else {
                Alert.alert("Payment Failed", "An unknown error occurred.");
            }
        }
    };

    return <Button title="Pay with Apple Pay" onPress={handleApplePay} />;
};

export default ApplePayButton;
