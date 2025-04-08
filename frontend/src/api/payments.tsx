import React, { useState } from "react";
import { 
    View, 
    Text, 
    TextInput, 
    Button, 
    Alert, 
    ActivityIndicator, 
    StyleSheet 
} from "react-native";
import { Picker } from "@react-native-picker/picker";
import axios from "axios";
import { useNavigation } from "@react-navigation/native";

const API_BASE_URL = "https://worldttance.com/WorldTtance"; // Updated to the new domain

interface PaymentResponse {
    payment_link?: string;
    error?: string;
}

const PaymentsScreen: React.FC = () => {
    const navigation = useNavigation();

    // Define state with proper types
    const [recipient, setRecipient] = useState("");
    const [amount, setAmount] = useState("");
    const [currency, setCurrency] = useState("USD");
    const [paymentMethod, setPaymentMethod] = useState("M-Pesa");
    const [country, setCountry] = useState("");
    const [phoneNumber, setPhoneNumber] = useState("");
    const [loading, setLoading] = useState(false);

    const isMPesa = paymentMethod === "M-Pesa";

    const handlePayment = async () => {
        if (!recipient || !amount || !currency || !paymentMethod || !country) {
            Alert.alert("Error", "Please fill in all required fields.");
            return;
        }

        if (isMPesa && !phoneNumber) {
            Alert.alert("Error", "Please enter a phone number for M-Pesa transactions.");
            return;
        }

        const numericAmount = parseFloat(amount);
        if (isNaN(numericAmount) || numericAmount <= 0) {
            Alert.alert("Error", "Please enter a valid amount.");
            return;
        }

        const formData = {
            recipient,
            amount: numericAmount, // Ensuring it's a valid number
            currency: currency.toUpperCase(),
            payment_method: paymentMethod,
            country,
            phone_number: isMPesa ? phoneNumber : null,
        };

        try {
            setLoading(true);
            const response = await axios.post<PaymentResponse>(`${API_BASE_URL}/api/flutterwave/initiate-payment/`, formData, {
                headers: { "Content-Type": "application/json" },
            });

            setLoading(false);

            if (response.data.payment_link) {
                Alert.alert("Success", "Redirecting to payment...");
                navigation.navigate("WebViewScreen" as never, { url: response.data.payment_link } as never);
            } else {
                Alert.alert("Error", response.data.error || "Unknown error");
            }
        } catch (error: any) {
            setLoading(false);
            console.error("Payment Request Error:", error);
            Alert.alert("Payment request failed", error.response?.data?.error || "An error occurred");
        }
    };

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Make a Payment</Text>

            <TextInput style={styles.input} placeholder="Recipient ID" value={recipient} onChangeText={setRecipient} />
            <TextInput style={styles.input} placeholder="Amount" keyboardType="numeric" value={amount} onChangeText={setAmount} />
            <TextInput style={styles.input} placeholder="Currency (e.g., USD, KES, EUR)" value={currency} onChangeText={setCurrency} autoCapitalize="characters" />
            <TextInput style={styles.input} placeholder="Country" value={country} onChangeText={setCountry} />

            {/* Payment Method Selection */}
            <Text style={styles.label}>Select Payment Method:</Text>
            <Picker
                selectedValue={paymentMethod}
                style={styles.picker}
                onValueChange={(itemValue) => setPaymentMethod(itemValue)}
            >
                <Picker.Item label="M-Pesa" value="M-Pesa" />
                <Picker.Item label="Card (Visa, MasterCard, Amex)" value="Card" />
                <Picker.Item label="Bank Transfer" value="Bank Transfer" />
                <Picker.Item label="Cryptocurrency (Bitcoin, Binance, etc.)" value="Cryptocurrency" />
                <Picker.Item label="Google Pay" value="Google Pay" />
                <Picker.Item label="Apple Pay" value="Apple Pay" />
            </Picker>

            {/* Show phone number input if M-Pesa is selected */}
            {isMPesa && (
                <TextInput
                    style={styles.input}
                    placeholder="Phone Number (e.g., +254...)"
                    keyboardType="phone-pad"
                    value={phoneNumber}
                    onChangeText={setPhoneNumber}
                />
            )}

            {loading ? (
                <ActivityIndicator size="large" color="#1E90FF" />
            ) : (
                <Button title="Proceed to Payment" onPress={handlePayment} color="#1E90FF" />
            )}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "#f4f4f4",
        padding: 20,
    },
    title: {
        fontSize: 22,
        fontWeight: "bold",
        marginBottom: 20,
        color: "#333",
    },
    label: {
        fontSize: 16,
        fontWeight: "bold",
        marginTop: 10,
        color: "#333",
    },
    input: {
        width: "100%",
        padding: 10,
        marginVertical: 8,
        borderWidth: 1,
        borderColor: "#ccc",
        borderRadius: 8,
        backgroundColor: "#fff",
    },
    picker: {
        width: "100%",
        height: 50,
        marginVertical: 8,
        backgroundColor: "#fff",
        borderWidth: 1,
        borderColor: "#ccc",
        borderRadius: 8,
    },
});

export default PaymentsScreen;
