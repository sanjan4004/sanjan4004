import React, { useState } from "react";
import { View, Text, TextInput, Button, StyleSheet, Alert } from "react-native";
import { initiatePayment } from "../src/api/initiatePayment";
import { useNavigation } from "@react-navigation/native";

const CheckoutScreen = () => {
    const navigation = useNavigation();
    const [recipient, setRecipient] = useState("");
    const [amount, setAmount] = useState("");
    const [currency, setCurrency] = useState("USD");
    const [paymentMethod, setPaymentMethod] = useState("card");
    const [country, setCountry] = useState("US");
    const [phoneNumber, setPhoneNumber] = useState("");

    const validateForm = () => {
        if (!recipient || !amount || isNaN(parseFloat(amount)) || parseFloat(amount) <= 0) {
            Alert.alert("Error", "Please enter a valid recipient and amount.");
            return false;
        }

        if (paymentMethod.toLowerCase() === "m-pesa" && !phoneNumber) {
            Alert.alert("Error", "Please enter a phone number for M-Pesa.");
            return false;
        }

        const validMethods = [
            "card",
            "m-pesa",
            "mobile_money",
            "bank",
            "bank_transfer",
            "crypto",
            "cryptocurrency",
            "google_pay",
            "apple_pay"
        ];

        if (!validMethods.includes(paymentMethod.toLowerCase())) {
            Alert.alert("Error", `Invalid payment method selected: ${paymentMethod}`);
            return false;
        }

        return true;
    };

    const handlePayment = async () => {
        if (validateForm()) {
            try {
                const response = await initiatePayment(
                    recipient,
                    parseFloat(amount),
                    currency,
                    paymentMethod,
                    country,
                    phoneNumber
                );

                if (response.success) {
                    Alert.alert("Payment Success", "Payment initiated successfully!");
                    navigation.replace("SuccessScreen");
                } else {
                    Alert.alert("Payment Failed", response.message || "Something went wrong.");
                    navigation.replace("FailureScreen");
                }
            } catch (error) {
                console.error("Payment initiation failed", error);
                Alert.alert("Error", "Something went wrong with the payment.");
            }
        }
    };

    return (
        <View style={styles.container}>
            <Text style={styles.label}>Recipient:</Text>
            <TextInput
                style={styles.input}
                value={recipient}
                onChangeText={setRecipient}
                placeholder="Enter recipient"
            />

            <Text style={styles.label}>Amount:</Text>
            <TextInput
                style={styles.input}
                value={amount}
                onChangeText={setAmount}
                placeholder="Enter amount"
                keyboardType="numeric"
            />

            <Text style={styles.label}>Currency:</Text>
            <TextInput
                style={styles.input}
                value={currency}
                onChangeText={setCurrency}
                placeholder="Currency (e.g., USD, EUR)"
            />

            <Text style={styles.label}>Payment Method:</Text>
            <TextInput
                style={styles.input}
                value={paymentMethod}
                onChangeText={setPaymentMethod}
                placeholder="e.g., card, m-pesa, bank_transfer, crypto, google_pay, apple_pay"
            />

            <Text style={styles.label}>Country:</Text>
            <TextInput
                style={styles.input}
                value={country}
                onChangeText={setCountry}
                placeholder="Enter country"
            />

            {paymentMethod.toLowerCase() === "m-pesa" && (
                <>
                    <Text style={styles.label}>Phone Number:</Text>
                    <TextInput
                        style={styles.input}
                        value={phoneNumber}
                        onChangeText={setPhoneNumber}
                        placeholder="Phone for M-Pesa"
                        keyboardType="numeric"
                    />
                </>
            )}

            <Button title="Pay Now" onPress={handlePayment} color="#007bff" />
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 20,
        backgroundColor: "#fff",
    },
    label: {
        fontSize: 16,
        marginBottom: 5,
        color: "#333",
    },
    input: {
        borderWidth: 1,
        borderColor: "#ccc",
        padding: 10,
        marginBottom: 20,
        borderRadius: 5,
    },
});

export default CheckoutScreen;
