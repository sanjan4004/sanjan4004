import React, { useEffect, useState } from "react";
import { View, Text, Button, Image, Alert, ActivityIndicator, StyleSheet } from "react-native";
import { useRoute, useNavigation } from "@react-navigation/native";
import { StackNavigationProp } from "@react-navigation/stack";
import { RouteProp } from "@react-navigation/native";
import { RootStackParamList } from "../App";
import { updateTransaction } from "../src/api/api/updateTransaction"; // Ensure correct API import

// Define route and navigation types
type SuccessScreenRouteProp = RouteProp<RootStackParamList, "SuccessScreen">;
type SuccessScreenNavigationProp = StackNavigationProp<RootStackParamList, "SuccessScreen">;

type Props = {};

const SuccessScreen: React.FC<Props> = () => {
    const route = useRoute<SuccessScreenRouteProp>();
    const navigation = useNavigation<SuccessScreenNavigationProp>();
    const { transactionId } = route.params; // Retrieve transaction ID
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const updatePaymentStatus = async () => {
            setLoading(true);
            try {
                // Update the transaction status to 'successful'
                if (transactionId) {
                    await updateTransaction({ transaction_id: transactionId, status: "successful" });
                    console.log("Transaction status updated to successful");
                }
            } catch (error) {
                Alert.alert("Error", "Failed to update transaction. Please check your connection.");
                console.error("Transaction update error:", error);
            } finally {
                setLoading(false);
            }
        };

        if (transactionId) {
            updatePaymentStatus();
        }
    }, [transactionId]);

    return (
        <View style={styles.container}>
            <Image source={require("../assets/success.png")} style={styles.image} />
            <Text style={styles.title}>Payment Successful 🎉</Text>
            <Text style={styles.message}>Your transaction was completed successfully.</Text>
            {loading ? (
                <ActivityIndicator size="large" color="#1E90FF" />
            ) : (
                <Button title="Go to Dashboard" onPress={() => navigation.navigate("HomeScreen")} />
            )}
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
        width: 100,
        height: 100,
        marginBottom: 20,
    },
    title: {
        fontSize: 20,
        fontWeight: "bold",
        color: "green",
        marginBottom: 10,
    },
    message: {
        fontSize: 16,
        textAlign: "center",
        marginBottom: 20,
    },
});

export default SuccessScreen;
