import React, { useEffect } from "react";
import { View, Text, Button, Image, Alert, StyleSheet } from "react-native";
import { useRoute, useNavigation, RouteProp } from "@react-navigation/native";
import { StackNavigationProp } from "@react-navigation/stack";
import { RootStackParamList } from "../App";  // Adjust the path if needed
import { updateTransaction } from "../src/api/api/updateTransaction";  // Adjust path accordingly

// TypeScript types for route and navigation
type FailureScreenRouteProp = RouteProp<RootStackParamList, "FailureScreen">;
type FailureScreenNavigationProp = StackNavigationProp<RootStackParamList, "FailureScreen">;

const FailureScreen: React.FC = () => {
    // Getting route and navigation props
    const route = useRoute<FailureScreenRouteProp>();
    const navigation = useNavigation<FailureScreenNavigationProp>();

    // Extract transaction ID from route params
    const { transactionId } = route.params || {};

    useEffect(() => {
        if (transactionId) {
            // Handle transaction failure when screen loads
            handleTransactionFailure(transactionId);
        }
    }, [transactionId]);

    // Update the transaction status to "failed"
    const handleTransactionFailure = async (transactionId: string) => {
        try {
            await updateTransaction({ transaction_id: transactionId, status: "failed" });
            console.log("Transaction updated to failed:", transactionId);
        } catch (error) {
            Alert.alert("Error", "Failed to update transaction status.");
            console.error("Transaction update failed:", error);
        }
    };

    return (
        <View style={styles.container}>
            <Image source={require("../assets/failure.png")} style={styles.image} />
            <Text style={styles.title}>Payment Failed</Text>
            <Text style={styles.message}>Your transaction could not be completed.</Text>
            <Button title="Try Again" onPress={() => navigation.navigate("PaymentScreen")} color="red" />
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "#ffe0e0",
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
        color: "red",
        marginBottom: 10,
    },
    message: {
        fontSize: 16,
        textAlign: "center",
        marginBottom: 20,
        color: "#333",
    },
});

export default FailureScreen;
