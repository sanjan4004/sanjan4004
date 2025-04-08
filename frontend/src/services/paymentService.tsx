import React, { useState } from "react";
import { 
    View, 
    Text, 
    TextInput, 
    Button, 
    StyleSheet, 
    ActivityIndicator 
} from "react-native";
import { Picker } from "@react-native-picker/picker";
import { useNavigation } from "@react-navigation/native";
import { initiatePayment } from "../src/api/initiatePayment";

const paymentMethods = [
    { label: "M-Pesa", value: "M-Pesa" },
    { label: "Mobile Money", value: "Mobile Money" },
    { label: "Card (Visa, MasterCard, Amex)", value: "Card" },
    { label: "Bank Transfer", value: "bank transfer" },
    { label: "Cryptocurrency (bitcoin, binance, etc.)", value: "Cryptocurrency" },
    { label: "Google Pay", value: "google Pay" },
    { label: "Apple Pay", value: "apple Pay" },
];

const PaymentsScreen: React.FC = () => {
    const navigation = useNavigation();

    // State management
    const [recipient, setRecipient] = useState("");
    const [amount, setAmount] = useState("");
    const [currency, setCurrency] = useState("USD");
    const [paymentMethod, setPaymentMethod] = useState(paymentMethods[0].value);
    const [country, setCountry] = useState("");
    const [phoneNumber, setPhoneNumber] = useState("");
    const [loading, setLoading] = useState(false);

    const isPhoneRequired = ["M-Pesa", "Mobile Money"].includes(paymentMethod);

    const handlePayment = async () => {
        const numericAmount = parseFloat(amount);
        if (isNaN(numericAmount) || numericAmount <= 0) {
            alert("Please enter a valid amount.");
            return;
        }

        setLoading(true);
        await initiatePayment(
            recipient,
            numericAmount,
            currency.toUpperCase(),
            paymentMethod,
            country,
            isPhoneRequired ? phoneNumber : undefined,
            navigation
        );
        setLoading(false);
    };

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Make a Payment</Text>

            <TextInput 
                style={styles.input} 
                placeholder="Recipient ID" 
                value={recipient} 
                onChangeText={setRecipient} 
            />
            <TextInput 
                style={styles.input} 
                placeholder="Amount" 
                keyboardType="numeric" 
                value={amount} 
                onChangeText={setAmount} 
            />
            <TextInput 
                style={styles.input} 
                placeholder="Currency (e.g., USD, KES, EUR)" 
                value={currency} 
                onChangeText={setCurrency} 
                autoCapitalize="characters" 
            />
            <TextInput 
                style={styles.input} 
                placeholder="Country" 
                value={country} 
                onChangeText={setCountry} 
            />

            {/* Payment Method Selection */}
            <Text style={styles.label}>Select Payment Method:</Text>
            <Picker
                selectedValue={paymentMethod}
                style={styles.picker}
                onValueChange={(itemValue) => setPaymentMethod(itemValue)}
            >
                {paymentMethods.map((method) => (
                    <Picker.Item key={method.value} label={method.label} value={method.value} />
                ))}
            </Picker>

            {/* Show phone number input if needed */}
            {isPhoneRequired && (
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
