import React, { useState, useEffect } from "react";
import { View, Text, TextInput, Button, ActivityIndicator, Alert, StyleSheet, Image } from "react-native";
import { WebView } from "react-native-webview";
import { useNavigation } from "@react-navigation/native";
import { initiateFlutterwavePayment, updateTransaction, checkTransactionStatus } from "../src/api/api";
import AsyncStorage from "@react-native-async-storage/async-storage";
import Logo from "@assets/logo.png";
import { Picker } from "@react-native-picker/picker";

// Fetch recipients
const fetchRecipients = async () => {
    try {
        const response = await fetch("https://worldttance.com/WorldTtance/recipients");
        const data = await response.json();
        return data.recipients || [];
    } catch (error) {
        console.error("Error fetching recipients:", error);
        return [];
    }
};

const PaymentScreen = () => {
    const navigation = useNavigation();
    const [checkoutUrl, setCheckoutUrl] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [recipients, setRecipients] = useState<any[]>([]);
    const [selectedRecipient, setSelectedRecipient] = useState<string | null>(null);
    const [amount, setAmount] = useState<string>("");
    const [transactionId, setTransactionId] = useState<string | null>(null);
    const [paymentMethod, setPaymentMethod] = useState<string>("card");
    const [userToken, setUserToken] = useState<string | null>(null);

    useEffect(() => {
        const getUserToken = async () => {
            const token = await AsyncStorage.getItem("userToken");
            setUserToken(token);
        };
        getUserToken();

        const getRecipients = async () => {
            const recipientList = await fetchRecipients();
            setRecipients(recipientList);
            if (recipientList.length > 0) {
                setSelectedRecipient(recipientList[0].id);
            }
        };
        getRecipients();
    }, []);

    const createTransaction = async (numericAmount: number) => {
        try {
            const response = await fetch("https://worldttance.com/WorldTtance/transactions/new", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${userToken}`,
                },
                body: JSON.stringify({
                    amount: numericAmount,
                    currency: "KES",
                    payment_method: paymentMethod,
                    recipient: { id: selectedRecipient },
                }),
            });

            const data = await response.json();

            if (data.status === "success") {
                setTransactionId(data.transaction_id);
                return data.transaction_id;
            } else {
                Alert.alert("Transaction Failed", data.message);
                return null;
            }
        } catch (error) {
            console.error("Transaction Error:", error);
            Alert.alert("Error", "Transaction creation failed!");
            return null;
        }
    };

    const handlePayment = async () => {
        if (!selectedRecipient || !amount) {
            Alert.alert("Error", "Please select a recipient and enter a valid amount.");
            return;
        }

        const numericAmount = parseFloat(amount);
        if (isNaN(numericAmount) || numericAmount <= 0) {
            Alert.alert("Error", "Amount must be a positive number.");
            return;
        }

        setLoading(true);

        try {
            const transactionId = await createTransaction(numericAmount);
            if (!transactionId) {
                setLoading(false);
                return;
            }

            const formData = {
                amount: numericAmount,
                currency: "USD",
                recipient: selectedRecipient,
                payment_method: paymentMethod,
            };

            const response = await initiateFlutterwavePayment(formData);

            if (response?.payment_link) {
                setCheckoutUrl(response.payment_link);
            } else {
                Alert.alert("Payment Failed", response?.error || "Unknown error");
                await updateTransaction({ transaction_id: transactionId, status: "failed" });
            }
        } catch (error) {
            console.error("Payment Error:", error);
            Alert.alert("Error", "Something went wrong. Please try again.");
            await updateTransaction({ transaction_id: transactionId, status: "failed" });
        } finally {
            setLoading(false);
        }
    };

    const handleNavigationStateChange = async (navState: any) => {
        if (navState.url.includes("payment-success")) {
            // Successful Payment
            await updateTransaction({ transaction_id: transactionId, status: "successful" });
            navigation.replace("SuccessScreen");
        } else if (navState.url.includes("payment-failed")) {
            // Payment Failed
            await updateTransaction({ transaction_id: transactionId, status: "failed" });
            navigation.replace("FailureScreen");
        }
    };

    useEffect(() => {
        const interval = setInterval(async () => {
            if (transactionId) {
                const statusResponse = await checkTransactionStatus(transactionId);
                if (statusResponse.status === "successful") {
                    clearInterval(interval);
                    navigation.replace("SuccessScreen");
                } else if (statusResponse.status === "failed") {
                    clearInterval(interval);
                    navigation.replace("FailureScreen");
                }
            }
        }, 5000);

        return () => clearInterval(interval); // Cleanup on unmount
    }, [transactionId]);

    if (checkoutUrl) {
        return (
            <WebView
                source={{ uri: checkoutUrl }}
                onNavigationStateChange={handleNavigationStateChange}
                startInLoadingState
                renderLoading={() => <ActivityIndicator size="large" color="#1E90FF" />}
            />
        );
    }

    return (
        <View style={styles.container}>
            <Image source={Logo} style={styles.logo} />
            <Text style={styles.title}>Make a Payment</Text>
            <Picker selectedValue={selectedRecipient} onValueChange={(itemValue) => setSelectedRecipient(itemValue)} style={styles.picker}>
                {recipients.map((recipient) => (
                    <Picker.Item key={recipient.id} label={recipient.name} value={recipient.id} />
                ))}
            </Picker>
            <Picker selectedValue={paymentMethod} onValueChange={(itemValue) => setPaymentMethod(itemValue)} style={styles.picker}>
                <Picker.Item label="Card" value="card" />
                <Picker.Item label="Google Pay" value="google_pay" />
                <Picker.Item label="Apple Pay" value="apple_pay" />
                <Picker.Item label="Bank Transfer" value="bank_transfer" />
                <Picker.Item label="Cryptocurrency" value="crypto" />
                <Picker.Item label="M-Pesa" value="mpesa" />
                <Picker.Item label="Mobile Money" value="mobile_money" />
            </Picker>
            <TextInput
                style={styles.input}
                placeholder="Enter Amount"
                keyboardType="numeric"
                value={amount}
                onChangeText={setAmount}
            />
            {loading ? (
                <ActivityIndicator size="large" color="#1E90FF" />
            ) : (
                <Button title="Pay Now" onPress={handlePayment} color="#1E90FF" disabled={!amount} />
            )}
        </View>
    );
};

const styles = StyleSheet.create({
    container: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#f4f4f4", padding: 20 },
    logo: { width: 120, height: 120, marginBottom: 10, resizeMode: "contain" },
    title: { fontSize: 22, fontWeight: "bold", marginBottom: 20, color: "#333" },
    picker: { width: "80%", height: 50, marginBottom: 20 },
    input: { width: "80%", height: 50, borderColor: "#ccc", borderWidth: 1, borderRadius: 8, paddingHorizontal: 10, fontSize: 18, marginBottom: 20, backgroundColor: "#fff" },
});

export default PaymentScreen;
