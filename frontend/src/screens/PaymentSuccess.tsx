import React, { useEffect } from "react";
import { View, Text, Button, Image, Alert, StyleSheet } from "react-native";
import { useRoute, useNavigation, RouteProp } from "@react-navigation/native";
import { StackNavigationProp } from "@react-navigation/stack";
import { RootStackParamList } from "../../App";
import { updateTransaction } from "../src/api/api/updateTransaction";

type PaymentSuccessRouteProp = RouteProp<RootStackParamList, "PaymentSuccess">;
type PaymentSuccessNavigationProp = StackNavigationProp<RootStackParamList, "PaymentSuccess">;

const PaymentSuccess: React.FC = () => {
    const route = useRoute<PaymentSuccessRouteProp>();
    const navigation = useNavigation<PaymentSuccessNavigationProp>();
    const { transactionId } = route.params || {};

    useEffect(() => {
        if (transactionId) {
            handleTransactionSuccess(transactionId);
        }
    }, [transactionId]);

    const handleTransactionSuccess = async (transactionId: string) => {
        try {
            await updateTransaction({ transaction_id: transactionId, status: "successful" });
            console.log("Transaction updated to successful:", transactionId);
        } catch (error) {
            Alert.alert("Error", "Failed to update transaction status.");
            console.error("Transaction update failed:", error);
        }
    };

    return (
        <View style={styles.container}>
            <Image source={require("../assets/success.png")} style={styles.image} />
            <Text style={styles.title}>Payment Successful </Text>
            <Text style={styles.message}>Your transaction was successfully completed.</Text>
            <Button title="Go to Home" onPress={() => navigation.navigate("Home")} color="green" />
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "#e0ffe0",
        padding: 20,
    },
    image: {
        width: 120,
        height: 120,
        marginBottom: 20,
    },
    title: {
        fontSize: 22,
        fontWeight: "bold",
        color: "green",
        marginBottom: 10,
    },
    message: {
        fontSize: 16,
        textAlign: "center",
        marginBottom: 20,
        color: "#333",
    },
});

export default PaymentSuccess;
